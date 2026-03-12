# Build all conda packages in dependency order

# Check for conda-build
try {
    conda build --version | Out-Null
} catch {
    Write-Error "conda-build is not installed. Please run: conda install conda-build"
    exit 1
}

$channel = "local"
# Use the default conda-bld directory or a local one
# Using default ensures subsequent builds can find the packages
$output_folder = "conda-bld"
if (!(Test-Path -Path $output_folder)) {
    New-Item -ItemType Directory -Force -Path $output_folder
}

function Build-Package {
    param (
        [string]$Name
    )
    Write-Host "Building $Name..."
    # We use --output-folder to keep artifacts local for easy finding,
    # but conda-build also installs them to the local cache for dependency resolution
    conda build conda_recipes\$Name --output-folder $output_folder -c conda-forge -c bioconda --no-anaconda-upload
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build $Name"
        exit 1
    }
}

# 1. Core (dependency for all)
Build-Package "bio-analyze-core"

# 2. Plot (dependency for rna-seq)
Build-Package "bio-analyze-plot"

# 3. Docking (independent of plot/rna-seq)
Build-Package "bio-analyze-docking"

# 4. RNA-Seq (depends on plot)
Build-Package "bio-analyze-rna-seq"

# 5. CLI
Build-Package "bio-analyze-cli"

Write-Host "All packages built successfully!"
Write-Host "Packages are located in: $output_folder\win-64"
Write-Host "To upload, run: anaconda upload $output_folder\win-64\bio-analyze-*.tar.bz2"
