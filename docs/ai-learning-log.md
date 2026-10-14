# Engineer A — AI Learning Log

## Learning Cycle 1: Validation

### Question
Why should input be validated before modifying a dictionary?

### AI explanation
Validation checks whether input meets the application's rules.
Validating before mutation prevents rejected input from leaving
an invalid record in storage.

### My experiment
I tried to create a request with a blank fellow ID.

Expected result: ValueError and no new record.

Actual result: [Write your actual result here.]

### Verification
Test run: [Write the test result here.]

### My decision
[Explain what I learned and whether the code worked as expected.]


## Learning Cycle 2: JSON Persistence

### Question
How can I load JSON without losing valid in-memory records
when the file is corrupted?

### AI explanation
Read the file, parse it, and validate every record in temporary
storage. Replace existing records only after the entire file
passes validation.

### My experiment
I created a valid request and then tried loading corrupted JSON.

Expected result: Loading fails and the existing request remains.

Actual result: [Write your actual result here.]

### Verification
Test run: [Write the test result here.]

### My decision
[Explain what I learned and whether I changed anything.]