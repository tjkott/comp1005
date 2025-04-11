// EMAS Record Pool Organiser by Tj
// INSTRUCTIONS:
// (1) Click run
// (2) Make sure the drop down thing 2 buttons to the right of "Run" button says "organiseFiles" instead of "calculateSimilarity"

function organiseFiles() {
    const startTime = new Date().getTime();
  
    // Folder names
    var rootFolderName = "EMAS_record_pool";
    var uploadFolderName = "UploadHere!!";
  
    Logger.log("=== EXECUTION START ===");
    Logger.log("Looking for root folder: " + rootFolderName);
    
    // Get root folder
    var rootFolders = DriveApp.getFoldersByName(rootFolderName);
    if (!rootFolders.hasNext()) {
      Logger.log("ERROR: Root folder not found. Please create a folder named '" + rootFolderName + "' in your Google Drive.");
      return;
    }
    var rootFolder = rootFolders.next();
    Logger.log("✅ Root folder found: " + rootFolder.getName() + " (ID: " + rootFolder.getId() + ")");
  
    // Get upload folder 
    Logger.log("Looking for upload folder: " + uploadFolderName + " within " + rootFolderName);
    var uploadFolders = rootFolder.getFoldersByName(uploadFolderName);
    if (!uploadFolders.hasNext()) {
      Logger.log("ERROR: Upload folder not found. Please create a folder named '" + uploadFolderName + "' in your root folder.");
      return;
    }
    var uploadFolder = uploadFolders.next();
    Logger.log("✅ Upload folder found: " + uploadFolder.getName() + " (ID: " + uploadFolder.getId() + ")");
  
    // Get sheet data - THIS IS WHERE THE ERROR IS HAPPENING
    var sheet;
    var data;
    
    try {
      // OPTION 1: Try to get all sheets and list them
      Logger.log("Checking available sheets in the active spreadsheet:");
      var allSheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
      
      if (allSheets.length === 0) {
        Logger.log("ERROR: No sheets found in the active spreadsheet.");
        return;
      }
      
      // List all available sheets
      for (var i = 0; i < allSheets.length; i++) {
        Logger.log(" - Sheet found: " + allSheets[i].getName());
      }
      
      // OPTION 2: Try to use the first sheet if SpotifyPlaylistAnalysis doesn't exist
      Logger.log("Attempting to use the first sheet if target sheet doesn't exist...");
      sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("SpotifyPlaylistAnalysis");
      
      if (!sheet) {
        Logger.log("'SpotifyPlaylistAnalysis' sheet not found. Using the first sheet instead.");
        sheet = allSheets[0];
        Logger.log("Using sheet: " + sheet.getName());
      } else {
        Logger.log("✅ Found 'SpotifyPlaylistAnalysis' sheet");
      }
      
      // Get data from selected sheet
      data = sheet.getDataRange().getValues();
      Logger.log("✅ Sheet data loaded: " + (data.length - 1) + " rows (excluding header row)");
      
      // Verify the data structure
      Logger.log("Checking data structure...");
      if (data.length <= 1) {
        Logger.log("ERROR: Sheet appears to be empty or has only a header row.");
        return;
      }
      
      // Check for required columns (column 1 should be song name, 5 should be genre, 6 should be parent genre)
      Logger.log("Header row: " + JSON.stringify(data[0]));
      Logger.log("First data row: " + JSON.stringify(data[1]));
      
      // Check if we have enough columns
      if (data[0].length < 7) {
        Logger.log("WARNING: Sheet doesn't have enough columns. Expected at least 7, found " + data[0].length);
        Logger.log("Column mappings will be adjusted to available data.");
      }
      
    } catch (e) {
      Logger.log("ERROR accessing spreadsheet: " + e.toString());
      return;
    }
  
    // Make manual review folder
    Logger.log("Checking for 'NeedsManualReview!!!' folder");
    var uncategorisedParent;
    var uncategorisedFolders = rootFolder.getFoldersByName("NeedsManualReview!!!");
    if (!uncategorisedFolders.hasNext()) {
      Logger.log("Creating 'NeedsManualReview!!!' folder");
      try {
        uncategorisedParent = rootFolder.createFolder("NeedsManualReview!!!");
        Logger.log("✅ Created NeedsManualReview!!! folder");
      } catch (e) {
        Logger.log("ERROR creating NeedsManualReview!!! folder: " + e.toString());
        return;
      }
    } else {
      uncategorisedParent = uncategorisedFolders.next();
      Logger.log("✅ Found existing NeedsManualReview!!! folder");
    }
  
    // Store all files in memory to avoid iterator exhaustion
    Logger.log("Loading files from upload folder...");
    var uploadFiles = [];
    try {
      var fileIterator = uploadFolder.getFiles();
      while (fileIterator.hasNext()) {
        var file = fileIterator.next();
        uploadFiles.push({
          file: file, 
          name: file.getName(),
          nameLower: file.getName().replace(/\.[^/.]+$/, "").toLowerCase()
        });
      }
      
      Logger.log("✅ Found " + uploadFiles.length + " files in upload folder");
      
      // If no files found, exit early
      if (uploadFiles.length === 0) {
        Logger.log("No files found in upload folder. Nothing to organize.");
        return;
      }
    } catch (e) {
      Logger.log("ERROR loading files from upload folder: " + e.toString());
      return;
    }
  
    // Track files that were moved
    var movedFiles = 0;
    var unmatchedSongs = [];
    var movedFileDetails = []; // Track which files were moved and where
    
    Logger.log("Starting to process songs from spreadsheet...");
  
    // Define column indices - these may need adjustment based on actual sheet layout
    // Default columns are 1 for song name, 5 for genre, 6 for parent genre
    var songNameColumn = 1;  // Column B (0-indexed)
    var genreColumn = 5;     // Column F (0-indexed)
    var parentGenreColumn = 6; // Column G (0-indexed)
    
    // Adjust column indices if we have fewer columns than expected
    if (data[0].length <= parentGenreColumn) {
      Logger.log("Adjusting column mappings due to sheet structure:");
      if (data[0].length <= genreColumn) {
        // Very limited sheet structure
        songNameColumn = 0; // Use first column for song name
        genreColumn = Math.min(1, data[0].length - 1); // Use second column for genre if available
        parentGenreColumn = Math.min(2, data[0].length - 1); // Use third column for parent genre if available
      } else {
        // Has genre but not parent genre
        parentGenreColumn = genreColumn; // Use the same column for both
      }
      Logger.log("Adjusted mappings - Song: column " + (songNameColumn+1) + 
                 ", Genre: column " + (genreColumn+1) + 
                 ", Parent Genre: column " + (parentGenreColumn+1));
    }
  
    // Process timeout check - Apps Script has a 6-minute execution time limit
    const maxExecutionTime = 5.5 * 60 * 1000; // 5.5 minutes in milliseconds
    
    for (var line = 1; line < data.length; line++) {
      // Check for timeout
      if (new Date().getTime() - startTime > maxExecutionTime) {
        Logger.log("WARNING: Approaching execution time limit. Stopping early at song " + line + " of " + (data.length - 1));
        break;
      }
      
      var songName = data[line][songNameColumn];
      if (!songName) {
        Logger.log("Skipping row " + line + " - no song name found");
        continue;
      }
      
      // Use the adjusted column indices for genre and parent genre
      var parentGenre = data[line][parentGenreColumn] ? String(data[line][parentGenreColumn]).split(",")[0].trim() : "";
      var genre = data[line][genreColumn] ? String(data[line][genreColumn]).split(",")[0].trim() : "";
      
      Logger.log("Processing song #" + line + ": " + songName + " (Genre: " + genre + ", Parent: " + parentGenre + ")");
  
      // Assign files with empty parent-genre/genre lines to (uncategorised)
      if (!parentGenre || !genre) {
        parentGenre = "NeedsManualReview!!!";
        genre = "NeedsManualReview!!!";
        Logger.log("Song has missing genre info - will place in NeedsManualReview!!!");
      }
  
      // Get or create parent genre folder
      var parentFolder;
      try {
        if (parentGenre === "NeedsManualReview!!!") {
          parentFolder = uncategorisedParent;
        } else {
          var parentFolders = rootFolder.getFoldersByName(parentGenre);
          if (!parentFolders.hasNext()) { 
            Logger.log("Creating parent genre folder: " + parentGenre);
            parentFolder = rootFolder.createFolder(parentGenre);
          } else {
            parentFolder = parentFolders.next();
          }
        }
      } catch (e) {
        Logger.log("ERROR creating parent genre folder '" + parentGenre + "': " + e.toString());
        continue; // Skip this song but continue processing others
      }
      
      // Get or create genre folder
      var genreFolder;
      try {
        if (genre === "NeedsManualReview!!!" && parentGenre === "NeedsManualReview!!!") {
          var genreFolders = uncategorisedParent.getFoldersByName("NeedsManualReview!!!");
          if (!genreFolders.hasNext()) {
            Logger.log("Creating genre folder in uncategorized: NeedsManualReview!!!");
            genreFolder = uncategorisedParent.createFolder("NeedsManualReview!!!");
          } else {
            genreFolder = genreFolders.next();
          }
        } else {
          var genreFolders = parentFolder.getFoldersByName(genre); 
          if(!genreFolders.hasNext()) {
            Logger.log("Creating genre folder: " + genre + " in " + parentFolder.getName());
            genreFolder = parentFolder.createFolder(genre);
          } else {
            genreFolder = genreFolders.next();
          }
        }
      } catch (e) {
        Logger.log("ERROR creating genre folder '" + genre + "': " + e.toString());
        continue; // Skip this song but continue processing others
      }
      
      // Calculate similarity for all remaining files
      var songNameLower = songName.toLowerCase();
      var bestMatch = { file: null, fileObj: null, score: 0.4 }; // Lower threshold to 0.4
      var closeMatches = [];
      
      for (var i = 0; i < uploadFiles.length; i++) {
        var fileObj = uploadFiles[i];
        var similarity = calculateSimilarity(songNameLower, fileObj.nameLower);
        
        // Log all similarities above 0.3 for debugging
        if (similarity > 0.3) {
          closeMatches.push({name: fileObj.name, similarity: similarity});
        }
        
        if (similarity > bestMatch.score) {
          bestMatch = {file: fileObj.file, fileObj: fileObj, score: similarity};
        }
      }
      
      // Log close matches for debugging
      if (closeMatches.length > 0) {
        Logger.log("Close matches for '" + songName + "':");
        for (var j = 0; j < closeMatches.length; j++) {
          Logger.log("  - " + closeMatches[j].name + " (" + (closeMatches[j].similarity * 100).toFixed(1) + "%)");
        }
      }
      
      // Check for duplicates and move file if match found
      if (bestMatch.file) {
        try {
          var existingFiles = genreFolder.getFilesByName(bestMatch.file.getName());
          if (!existingFiles.hasNext()) {
            try {
              // IMPORTANT: Add a small delay before moving files to prevent hitting rate limits
              Utilities.sleep(50);
              
              bestMatch.file.moveTo(genreFolder);
              Logger.log("✅ Moved: " + bestMatch.file.getName() + " (" + (bestMatch.score * 100).toFixed(1) + "% match to \"" + songName + "\")");
              
              // Track which file was moved where
              movedFileDetails.push({
                fileName: bestMatch.file.getName(),
                destination: parentGenre + "/" + genre,
                matchScore: (bestMatch.score * 100).toFixed(1) + "%"
              });
              
              // Remove the moved file from our array to avoid moving it again
              uploadFiles.splice(uploadFiles.indexOf(bestMatch.fileObj), 1);
              movedFiles++;
            } catch (e) {
              Logger.log("❌ Error moving file: " + bestMatch.file.getName() + " - " + e.toString());
            }
          } else {
            Logger.log("⚠️ Duplicate skipped: " + bestMatch.file.getName() + " (" + (bestMatch.score * 100).toFixed(1) + "% match)");
          }
        } catch (e) {
          Logger.log("❌ Error checking for duplicates: " + e.toString());
        }
      } else {
        Logger.log("⚠️ File not found: " + songName);
        unmatchedSongs.push(songName);
      }
    }
    
    // Summary
    const endTime = new Date().getTime();
    const executionTimeSeconds = ((endTime - startTime) / 1000).toFixed(2);
    
    Logger.log("\n===== SUMMARY =====");
    Logger.log("Total execution time: " + executionTimeSeconds + " seconds");
    Logger.log("Total songs in playlist: " + (data.length - 1));
    Logger.log("Total files moved: " + movedFiles);
    Logger.log("Files remaining in upload folder: " + uploadFiles.length);
    
    if (movedFileDetails.length > 0) {
      Logger.log("\nFiles moved successfully:");
      for (var n = 0; n < movedFileDetails.length; n++) {
        var detail = movedFileDetails[n];
        Logger.log("  - " + detail.fileName + " → " + detail.destination + " (Match: " + detail.matchScore + ")");
      }
    }
    
    if (unmatchedSongs.length > 0) {
      Logger.log("\nUnmatched songs (" + unmatchedSongs.length + "):");
      for (var k = 0; k < unmatchedSongs.length; k++) {
        Logger.log("  - " + unmatchedSongs[k]);
      }
    }
    
    if (uploadFiles.length > 0) {
      Logger.log("\nRemaining files in upload folder:");
      for (var m = 0; m < uploadFiles.length; m++) {
        Logger.log("  - " + uploadFiles[m].name);
      }
    }
    
    Logger.log("=== EXECUTION COMPLETE ===");
  }
  
  // Levenshtein's distance function for matching file names and song names
  function calculateSimilarity(str1, str2) {
    // Add null checks to prevent errors
    if (!str1 || !str2) return 0; 
    
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = [];
  
    // Initialize matrix
    for (let i = 0; i <= len1; i++) matrix[i] = [i];
    for (let j = 0; j <= len2; j++) matrix[0][j] = j; 
  
    for (let i = 1; i <= len1; i++) {
      for (let j = 1; j <= len2; j++) {
        const cost = str1[i-1] === str2[j-1] ? 0 : 1;
        matrix[i][j] = Math.min(
          matrix[i-1][j] + 1,        // deletion
          matrix[i][j-1] + 1,        // insertion
          matrix[i-1][j-1] + cost    // substitution
        );
      }
    }
    return 1 - (matrix[len1][len2] / Math.max(len1, len2));
  }