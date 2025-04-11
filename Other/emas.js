// Levenshtein's distance function for matching file names and song names
function calculateSimilarity(str1, str2) {
    const len1 = str1.length
    const len2 = str2.length;
    const matrix = [];

    // loop runs length of the string
    for (let i = 0; i <= len1; i++) matrix[i] = [i]; // for each iteration, initialises a new row in the matrix[i] and sets first element to 1. 
    for (let j = 0; j <= len2; j++) matrix[0][j] = j; // 

    for (let i = 1; i <= len1; i++) {
        for (let j = 1; j <= len2; j++) {
            const cost = str1[i-1] === str2[j-1] ? 0 : 1; // if the characters are the same, cost is 0, else cost is 1.
            matrix[i][j] = Math.min(matrix[i-1][j] + 1, // deletion
                                    matrix[i][j-1] + 1, // insertion
                                    matrix[i-1][j-1] + cost); // substitution
            }
        }
    return 1 - (matrix[len1][len2] / Math.max(len1, len2)); // returns the similarity score between 0 and 1.
}                        

function organiseFiles() {
    const howtoguide = '1xkvCFUoJx4Wr8FAa0WlqBba6o-hUnotptGaCSbKY5BE';

    // Folder names
    var rootFolderName = "EMAS_record_pool";
    var uploadFolderName = "UploadHere!!";

    // Get root folder
    var rootFolders = DriveApp.getFoldersByName(rootFolderName);
    if (!rootFolders.hasNext()) throw new Error("Upload folder not found.");
    var rootFolder = rootFolders.next();

    // Get upload folder 
    var uploadFolders = rootFolder.getFoldersByName(uploadFolderName);
    if (!uploadFolders.hasNext()) throw new Error("Upload folder not found. Please create a folder named 'UploadHere!!' in your Google Drive.");
    var UploadFolder = uploadFolders.next();

    //sheets
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("SpotifyPlaylistAnalysis");
    var data = sheet.getDataRange().getValues();

    //make manual review folder
    var uncategorisedParent = rootFolder.getFoldersByName("NeedsManualReview!!!");
    if (!uncategorisedParent.hasNext()) {
        uncategorisedParent = rootFolder.createFolder("NeedsManualReview!!!");
    } else {
        uncategorisedParent = uncategorisedParent.next();
    }

    // Cache all files in UploadFolder once
    var cachedFiles = [];
    var tempFiles = UploadFolder.getFiles();
    while (tempFiles.hasNext()) cachedFiles.push(tempFiles.next());

    

    for (var line = 1; line < data.length; line++) {
        var songName = data[line][1]
        var parentGenre = data[line][6].split(",")[0].trim()
        var genre = data[line][5].split(",")[0].trim() // Get the first genre in the list. 

        // Assign files with empty parent-genre/genre lines to (uncategorised)
        if (!parentGenre || !genre) {
            parentGenre = "NeedsManualReview!!!";
            genre = "NeedsManualReview!!!";
        }

        // Parent genre
        var parentFolder = rootFolder.getFoldersByName(parentGenre);
        if (parentGenre === "NeedsManualReview!!!") {
            parentFolder = uncategorisedParent;
        } else {
            parentFolder = driveFolder.getFoldersByName(parentGenre);
            if (!parentFolder.hasNext()) { 
                parentFolder = driveFolder.createFolder(parentGenre);
            } else {
                parentFolder = parentFolder.next();
            }
        }
        // Genre
        var genreFolder = parentFolder.getFoldersByName(genre);
        if (genre === "NeedsManualReview!!!" && parentGenre === "NeedsManualReview!!!") {
            genreFolder = uncategorisedParent.getFoldersByName("NeedsManualReview!!!");
            if (!genreFolder.hasNext()) {
                genreFolder = uncategorisedParent.createFolder("NeedsManualReview!!!");
            } else {
                genreFolder = genreFolder.next();
            }
        } else {
            genreFolder = parentFolder.getFoldersByName(genre); 
            if(!genreFolder.hasNext()) { // Create genre in the parent folder if it does not exist
                genreFolder = parentFolder.createFolder(genre);
            } else {
                genreFolder = genreFolder.next();
            }
        }
        // Move files to the genre folder enhanced with Levenshtein's distance function for matching file names
        var bestMatch = { file: null, score: 0 };

        for (var i = 0; i < cachedFiles.length; i++) {
            var file = cachedFiles[i];
            var fileName = file.getName().replace(/\.[^/.]+$/, "").toLowerCase(); // Remove file extensions and lower case. 
            var songNameLower = songName.toLowerCase();
            
            // Calculate similarity
            var similarity1 = calculateSimilarity(songNameLower, fileName); // Direct match
            var similarity2 = calculateSimilarity(songNameLower + ".mp3", file.getName().toLowerCase()); // Match with .mp3 extension
            var similarity3 = calculateSimilarity(songNameLower + ".wav", file.getName().toLowerCase()); // Match with .wav extension
            // Use the highest similarity score
            var similarity = Math.max(similarity1, similarity2, similarity3);
            if (similarity > bestMatch.score && similarity > 0.5) {
                bestMatch = {file: file, score: similarity};
            }
        }
        // Check for duplicates in the destination folder:
        if (bestMatch.file) {
            var existingFiles = genreFolder.getFilesByName(bestMatch.file.getName());
            if (!existingFiles.hasNext()) {
                bestMatch.file.moveTo(genreFolder); // Move the best match file to the genre folder
                Logger.log(`Moved: ${bestMatch.file.getName()} (${(bestMatch.score * 100).toFixed(1)}% match to "${songName}")`);
            } else {
                Logger.log(`Duplicate skipped: ${bestMatch.file.getName()} (${(bestMatch.score * 100).toFixed(1)}%)`);
            }
        } else {
            Logger.log(`⚠️ File not found: ${songName}`);
        }    
    }
  }
  