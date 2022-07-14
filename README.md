# Google Drive Asset Plugin for Katana

## This is an Asset Plugin for Katana written as part of learning C++ and the Foundry's Katana Asset API. 

### Caveat: 
This assumes that the Google Drive is mounted as G: drive locally.
Initially, I tried getting it working with the web version of Google Drive, but because of the number of calls the asset plugin makes 
to the Google APIs, it kept on hitting the API calls limit for Google Drive, which is why this decision was made. Unfortunately this means this can only
work on Windows.

### Project Folder Structure
This plugin assumes the following project folder structure at Root defined in the plugin:

```
<ProjectNAME> -- <Assets> -- <Asset_NAME> -- <Pipeline_STEP> -- <File_NAME>
         |
         |
          -- <Sequences> -- <Sequence_NAME> -- <File_NAME>
```

### Phase 2: 
I would like to integrate it with Google Sheets for the next iteration. Where we can create a sheet per project to act as an AMS database, 
which tracks the assets and shots. The asset plugin can update the sheet every time an asset/shot is published.
