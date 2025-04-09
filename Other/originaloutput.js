function organizeFiles() {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
    var data = sheet.getDataRange().getValues();
    var driveFolder = DriveApp.getFolderById("YOUR_FOLDER_ID"); // Replace with your folder ID

    for (var i = 1; i < data.length; i++) { // Skip header row
        var songName = data[i][0]; // Assuming song name is in column A
        var genre = data[i][1]; // Assuming genre is in column B

        var genreFolder = driveFolder.getFoldersByName(genre);
        if (!genreFolder.hasNext()) {
            genreFolder = driveFolder.createFolder(genre);
        } else {
            genreFolder = genreFolder.next();
        }

        var files = driveFolder.getFilesByName(songName);
        while (files.hasNext()) {
            var file = files.next();
            file.moveTo(genreFolder);
        }
    }
}


// 1. Get upload folder (from your existing code)
var uploadFolders = rootFolder.getFoldersByName(uploadFolderName);
if (!uploadFolders.hasNext()) throw new Error("Upload folder not found");
var UploadFolder = uploadFolders.next();

// 2. Modified file movement
var files = UploadFolder.getFilesByName(songName); // FIXED LINE
while (files.hasNext()) {
    var file = files.next();
    if (!genreFolder.getFilesByName(songName).hasNext()) {
        file.moveTo(genreFolder);
    } else {
        Logger.log("Duplicate skipped: " + songName);
    }
}
if (!files.hasNext()) {
    Logger.log("⚠️ File not found: " + songName);
}


// Enable Drive API in Resources > Advanced Google Services
function moveFilesBatch() {
    const batchSize = 100;
    const filesArray = [...]; // Array of file IDs
    for (let i = 0; i < filesArray.length; i += batchSize) {
        const batch = filesArray.slice(i, i + batchSize);
        Drive.Files.update({}, batch[0], null, {
            addParents: "FOLDER_ID",
            removeParents: UploadFolder.getId()
        });
    }
}
