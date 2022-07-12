#include <gdAsset.h>
#include <FnLogging/FnLogging.h>

#include <FnAttribute/FnAttribute.h>
#include <FnAttribute/FnGroupBuilder.h>

#include <sys/types.h>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <sstream>
#ifndef _WIN32
#include <pwd.h>
#endif
#include <boost/regex.hpp>

#include <pystring/pystring.h>

FnLogSetup("gdAsset");

const char* gdAsset::_typeAttributeKey("type");

gdAsset::gdAsset() : Asset()
{
	// something
}

gdAsset::~gdAsset()
{
	// nothing
}

FnKat::Asset* gdAsset::create()
{
	std::cout << "just created an asset"<<std::endl;   //del this
	return new gdAsset();
}

void gdAsset::reset()
{
	// nothing for now
}

bool gdAsset::isAssetId(const std::string& id)
{
	if (!pystring::startswith(id, GD_PREFIX))
	{
		return false;
	}
	if (id.find("Assets") != std::string::npos)
	{
		return true;
	}
	return false;
}

bool gdAsset::containsAssetId(const std::string& id)
{
	//again, everystring is a file path/assetid..for now atleast
	return true;
}

bool gdAsset::checkPermissions(const std::string& assetId, const StringMap& context)
{
	//ideally would like to verify with the gmail id(if foundry)
	return true;
}

bool gdAsset::runAssetPluginCommand(const std::string& assetId, const std::string& command, const StringMap& commandArgs)
{
	return true;
}

void gdAsset::resolveAsset(const std::string& id, std::string& asset)
{
	asset = id;
}

void gdAsset::resolveAllAssets(const std::string& id, std::string& assets)
{
	assets = id;
}

void gdAsset::resolvePath(const std::string& str, const int frame, std::string& ret)
{
	ret = str;

	//Resolve user(~) and env vars($)
	ret = _expandUser(ret);
	ret = _expandVars(ret);

	/*if (fnkat::defaultfilesequenceplugin::isfilesequence(ret))
	{
		ret = fnkat::defaultfilesequenceplugin::resolvefilesequence(ret, frame);
	}*/

	ret = str;
}

void gdAsset::resolveAssetVersion(const std::string& assetId, std::string& ret, const std::string& versionStr)
{
	ret = "";
}

void gdAsset::getAssetDisplayName(const std::string& assetId, std::string& ret)
{
	std::string head;
	pystring::os::path::split(head, ret, assetId);
}

void gdAsset::getAssetVersions(const std::string& assetId, StringVector& ret)
{
	// no version support yet.
	/*if (!isAssetId(assetId))
	{
		return;
	}
	pystring::*/

}

void gdAsset::getUniqueScenegraphLocationFromAssetId(
	const std::string & assetId,
	bool includeVersion,
	std::string& ret)
{
	std::vector<std::string> tokens;

	pystring::split(assetId.c_str(), tokens, "/");
	if (tokens.empty() || !tokens[0].empty())
	{
		tokens.insert(tokens.begin(), "");
	}

	for (unsigned int i = 1; i < tokens.size(); ++i)
	{
		tokens[i] = _getSafeIdentifier(tokens[i]);
	}

	ret = pystring::join("/", tokens);
}

void gdAsset::getRelatedAssetId(const std::string& assetId, const std::string& relation, std::string& ret)
{
	ret = "";
}

void gdAsset::getAssetFields(const std::string& assetId, bool includeDefaults, StringMap& returnFields)
{
	std::string directory;
	std::string filename;
	std::string ext;
	std::string version; //WAIT...
	std::vector<std::string> result;
	std::vector<std::string> splitted;

	pystring::os::path::split(directory, filename, assetId);
	pystring::os::path::splitext(filename, ext, filename);
	returnFields[kFnAssetFieldName] = filename;
	pystring::split(filename, splitted, "_");
	pystring::split(directory, result, "\\");

	returnFields["project"] = std::string(result[3]);
	returnFields["pipe_step"] = std::string(result.at(6));
	returnFields["entity"] = std::string(result.at(5));
	returnFields["entity_type"] = std::string(result.at(4));

}

void gdAsset::buildAssetId(const StringMap& fields, std::string& ret)
{	
	std::vector<std::string> ver_split;
	std::string file_no_ext;
	std::string ext;
	for (auto it = fields.cbegin(); it != fields.end(); ++it)
	{
		std::cout << it->first << " : " << it->second << "\n";
	}
	ret = GD_PREFIX;
	StringMap::const_iterator iter, itend = fields.end();
	
	StringMap::const_iterator iter_project = fields.find("project");
	if (iter_project != itend)
		ret += (*iter_project).second + "\\";

	StringMap::const_iterator iter_entity_type = fields.find("entity_type");
	if (iter_entity_type != itend)
		ret += (*iter_entity_type).second + "\\";

	StringMap::const_iterator iter_entity = fields.find("entity");
	if (iter_entity != itend)
		ret += (*iter_entity).second + "\\";

	StringMap::const_iterator iter_pipe_step = fields.find("pipe_step");
	if (iter_pipe_step != itend)
		ret += (*iter_pipe_step).second + "\\";
	
	StringMap::const_iterator iter_file_name = fields.find("name");

	if (fields.find("version") != fields.end())
	{
		StringMap::const_iterator iter_version = fields.find("version");
		pystring::os::path::splitext(file_no_ext, ext, (*iter_file_name).second);   //gets rid of the extension
		pystring::split(file_no_ext, ver_split, "_");								// splits the file name based on underscores and puts it in a list ver_split
		ver_split.pop_back();
		ret += pystring::join("_", ver_split) + "_" + (*iter_version).second + ext;

	}
	else {
		if (iter_file_name != itend)
			ret += (*iter_file_name).second;
		else {
			if ((*iter_pipe_step).second == "Lookdev"){
				ret += (*iter_entity).second + "_" + "ldv" + "_" + "v01";  //harcoded version, needs to be addressed
			}
		}
	}
}

void gdAsset::getAssetAttributes(const std::string& assetId, const std::string& scope, StringMap& returnAttrs)
{
	std::string root;
	std::string ext;
	const unsigned int REMOVE_DOT = 1;

	pystring::os::path::splitext(root, ext, assetId);

	if (ext.empty())
	{
		ext = "Unknown: File path ' ";
		ext += assetId;
		ext += "'";
		ext += " has no extension";
	}

	else
	{
		ext = ext.substr(REMOVE_DOT);
	}

	std::pair<std::string, std::string> entry(gdAsset::_typeAttributeKey, ext);

	returnAttrs.insert(entry);
}

void gdAsset::setAssetAttributes(const std::string& assetId, const std::string& scope, const StringMap& attrs)
{
	// nothing for now
}

void gdAsset::getAssetIdForScope(const std::string& assetId, const std::string& scope, std::string& ret)
{
	ret = assetId;
}

void gdAsset::createAssetAndPath(FnKat::AssetTransaction* txn, const std::string& assetType, const StringMap& assetFields, const StringMap& args, bool createDirectory, std::string& assetId)
{

	StringMap::const_iterator versionUpIt = args.find("versionUp");
	if (versionUpIt != args.end() && versionUpIt->second == "True")
	{
		std::vector<std::string> result;
		StringMap::const_iterator assetnameIt = assetFields.find("name");
		pystring::partition(assetnameIt->second, "_v", result);
		int version = stoi(result.back()) + 1; // increment the existing version
		StringMap newAssetFields = assetFields;
		newAssetFields.insert(std::pair<std::string, std::string> ("version", "v0" + std::to_string(version)));
		buildAssetId(newAssetFields, assetId);
	}
	else {
		buildAssetId(assetFields, assetId);
	}
	

	StringMap::const_iterator fileExtensionIt = args.find("fileExtension");

	if (fileExtensionIt != args.end())
	{
		if (fileExtensionIt->second.size() > 0)
		{
			const std::string fileExtension = "." + fileExtensionIt->second;
			if (!pystring::endswith(assetId, fileExtension))
			{
				std::cout << "ran this" << std::endl;
				assetId += fileExtension;
			}
		}
	}
	else
	{
		if (assetType == kFnAssetTypeKatanaScene)
		{
			if (!pystring::endswith(assetId, ".katana"))
			{
				assetId += ".katana";
			}
		}
		else if (assetType == kFnAssetTypeLookFile)
		{
			if (!pystring::endswith(assetId, ".klf"))
			{
				assetId += ".klf";
			}
		}
		else if (assetType == kFnAssetTypeFCurveFile)
		{
			if (!pystring::endswith(assetId, ".fcurve"))
			{
				assetId += ".fcurve";
			}
		}
		else if (assetType == kFnAssetTypeLiveGroup)
		{
			if (!pystring::endswith(assetId, ".livegroup"))
			{
				std::cout << "THE LIVEGROUP THING RAN" << std::endl;
				assetId += ".livegroup";
			}
		}
	}
}

void gdAsset::postCreateAsset(FnKat::AssetTransaction* txn, const std::string& assetType, const StringMap& assetFields, const StringMap& args, std::string& assetId)
{
	buildAssetId(assetFields, assetId);
}


// -- pvt helper methods ---//

std::string gdAsset::_getSafeIdentifier(const std::string& id)
{
	std::string result;
	std::string::const_iterator it = id.begin(), itEnd = id.end();
	for (; it != itEnd; ++it)
	{
		if (isalnum(*it) || *it == '_')
		{
			result += *it;
		}
		else
		{
			result += '_';
		}
	}

	if (result.empty())
	{
		result = "_";
	}

	if (!isalpha(result[0]) && result[0] != '_')
	{
		result = std::string("_") + result;
	}

	return result;
}

std::string gdAsset::_expandUser(const std::string& fileString)
{
	if (!pystring::startswith(fileString, "~"))
		return fileString;

	std::string userHome;

	int i = pystring::find(fileString, "/", 1);
	if (i < 0)
	{
		i = fileString.size();
	}
	if (i == 1)
	{
		char* homeenv = getenv("HOME");
		if (homeenv)
		{
			userHome = homeenv;
		}
		else
		{
#ifndef _WIN32
			struct passwd* pwd = getpwuid(getuid());
			if (pwd)
			{
				userHome = pwd->pw_dir;
			}
#endif
		}
		
	}
	else
	{
		std::string userName = pystring::slice(fileString, 1, i);
#ifndef _WIN32
		struct passwd* pwd = getpwnam(userName.c_str());
		if (pwd)
		{
			userHome = pwd->pw_dir;
		}
#endif
	}

	if (userHome.empty())
	{
		return fileString;
	}

	if (pystring::endswith(userHome, "/"))
	{
		i += 1;
	}

	return userHome + pystring::slice(fileString, i);
}

#if defined(__clang__)
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wexit-time-destructors"
#endif
static boost::regex g_varExp("\\$(\\w+|\\{[^}]*\\})",
	boost::regex::extended & ~boost::regex::collate);

#if defined(__clang__)
#pragma clang diagnostic pop
#endif

std::string gdAsset::_expandVars(const std::string& fileString)
{
	if (pystring::find(fileString, "$") < 0)
	{
		return fileString;
	}

	std::string returnString = fileString;

	int i = 0;
	int offset = 0;
	while (true)
	{
		boost::smatch m;
		std::string substring = returnString.substr(offset);
		if (!boost::regex_search(substring, m, g_varExp))
		{
			break;
		}

		// replace the match in returnString
		i = m.position() + offset;
		int j = m.position() + m.length() + offset;

		std::string name = pystring::slice(returnString, i + 1, j);

		if (pystring::startswith(name, "{") && pystring::endswith(name, "}"))
		{
			name = pystring::slice(name, 1, -1);
		}

		const char* nameEnv = getenv(name.c_str());
		if (nameEnv)
		{
			std::string tail = pystring::slice(returnString, j);
			returnString = pystring::slice(returnString, 0, i) + nameEnv;
			i = returnString.size();
			returnString += tail;
		}
		else
		{
			i = j;
			offset++;
		}
	};

	return returnString;
}

//-------REGISTER THE PLUGIN------\\

DEFINE_ASSET_PLUGIN(gdAsset)

void registerPlugins()
{
	REGISTER_PLUGIN(gdAsset, "Google", 0, 1);
}
