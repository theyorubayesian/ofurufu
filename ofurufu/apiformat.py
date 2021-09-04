# --------------
# Video Analyzer
# --------------
BASE = "https://api.videoindexer.ai/Auth/{location}/Accounts/{accountId}/"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Get-Account-Access-Token-With-Permission
# GET Request | Returns Token
ACCESS_TOKEN_WITH_PERMISSION = "AccessTokenWithPermission?permission={permission}"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Create-Person-Model
CREATE_PERSON_MODEL = "Customization/PersonModels?name={name}"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Create-Person
# POST Request 
CREATE_PERSON = "Customization/PersonModels/{personModelId}/Persons?name={name}"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Upload-Video
# POST Request | Returns VideoID
INDEX_VIDEO = "Videos?name={videoName}&privacy={privacy}&videoUrl={url}" \
                "&indexingPreset={indexingPreset}&sendSuccessEmail={successEmail}" \
                "&streamingPreset={streamingPreset}"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Get-Video-Index
# GET Request 
GET_VIDEO_INDEX = "Videos/{videoId}/Index"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Get-Video-Thumbnail
# GET Request 
GET_VIDEO_THUMBNAIL = "Videos/{videoId}/Thumbnails/{thumbnailId}?format={fmt}"

# https://api-portal.videoindexer.ai/api-details#api=Operations&operation=Create-Custom-Face
# POST Request | 
CREATE_FACE = "Customization/PersonModels/{personModelId}/Persons/{personId}/Faces"

# --------
# Face API
# --------
