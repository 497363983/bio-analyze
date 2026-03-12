param (
    [string]$TestPath = ""
)

if ($TestPath) {
    docker-compose -f docker-compose.test.yml run --rm bio-analyze-test $TestPath
} else {
    docker-compose -f docker-compose.test.yml run --rm bio-analyze-test packages
}
