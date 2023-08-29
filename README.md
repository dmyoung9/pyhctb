# pyhctb

This is an API layer for getting school bus transit coordinates from [Here Comes The Bus](https://herecomesthebus.com/).

To install this package, simply run:

```bash
pip install pyhctb
```

To use `pyhctb`, run the following command, replacing `USERNAME`, `PASSWORD`, and `SCHOOL_CODE` with your own credentials:

```bash
python -m pyhctb --user USERNAME --password PASSWORD --code SCHOOL_CODE
```

You should get a final output that looks something like the following (but with actual values):

```json
{
    "legacyID": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "name": "Johnny Everyboy",
    "timeSpanId": "ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj",
    "latitude": "70.92797",
    "longitude": "-74.29596"
}
```
