# Define the list of folders to process
$folders = @('sliding_window_1')

foreach ($folder in $folders) {
    Write-Host "Running predict_ml.py in folder '$folder'..."
    
    # Change directory into the target folder
    Push-Location $folder
    
    # Execute the Python script
    python predict_ml.py 1
    
    # Return to the original directory
    Pop-Location
    
    Write-Host "Waiting for 20 seconds before processing the next folder..."
    Start-Sleep -Seconds 20
}