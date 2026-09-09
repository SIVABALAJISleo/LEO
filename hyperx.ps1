param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

python -m hyper_x.cli $ArgsList
