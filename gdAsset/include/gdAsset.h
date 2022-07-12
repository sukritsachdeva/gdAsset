#ifndef GDASSET_H
#define GDASSET_H

#include<string>
#include<FnAsset/plugin/FnAsset.h>
#include<FnLogging/FnLogging.h>

class gdAsset : public FnKat::Asset
{
public:
	const std::string GD_PREFIX = "G:\\";
	gdAsset();
	virtual ~gdAsset();

	static FnKat::Asset* create();   //what exactly is happening here? why is this a static class?

	void reset();

	bool isAssetId(const std::string& name);
	bool containsAssetId(const std::string& name);

	bool checkPermissions(const std::string& assetId, const StringMap& context);
	bool runAssetPluginCommand(const std::string& assetId, const std::string& command, const StringMap& commandArgs);

	void resolveAsset(const std::string& assetId, std::string& ret);
	void resolveAllAssets(const std::string& str, std::string& ret);
	void resolvePath(const std::string& str, const int frame, std::string& ret);

	void resolveAssetVersion(const std::string& assetId, std::string& ret, const std::string& versionStr = std::string());

	void getUniqueScenegraphLocationFromAssetId(const std::string& assetId, bool includeVersion, std::string& ret);

	void getAssetDisplayName(const std::string& assetId, std::string& ret);
	void getAssetVersions(const std::string& assetId, StringVector& ret);

	void getRelatedAssetId(const std::string& assetId, const std::string& relation, std::string& ret);

	void getAssetFields(const std::string& assetId, bool includeDefaults, StringMap& returnFields);

	void buildAssetId(const StringMap& fields, std::string& ret);

	void getAssetAttributes(const std::string& assetId, const std::string& scope, StringMap& returnAttrs);

	void setAssetAttributes(const std::string& assetId, const std::string& scope, const StringMap& attrs);

	void getAssetIdForScope(const std::string& assetId, const std::string& scope, std::string& ret);

	void createAssetAndPath(FnKat::AssetTransaction* txn, const std::string& assetType, const StringMap& assetFields, const StringMap& args, bool createDirectory, std::string& assetId);

	void postCreateAsset(FnKat::AssetTransaction* txn, const std::string& assetType, const StringMap& assetFields, const StringMap& args, std::string& assetId);

	static void flush() {}

private:
	static const char* _typeAttributeKey;
	static std::string _getSafeIdentifier(const std::string& id);
	static std::string _expandUser(const std::string& fileString);
	static std::string _expandVars(const std::string& fileString);
};

#endif