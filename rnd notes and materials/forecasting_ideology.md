

## 19-09-2026

## forecasters abstraction ideology

Perfect:
takes
- timestamp 'at'
- horizon
returnes
- series slice on horizon after at (including)

Percistant (Naive):
- takes history
- returnes its copy
- or takes current value and returnes its copy

OpenSTEF GBLinear implementation:
takes
- takes timestamp 'at'
- some time-indexed pd.Series. interpreted as history immediately before 'at'
- horizon
returns
- time-indexed pd.Series on horizon after at (including)
interpreted as forecast