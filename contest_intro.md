# Proof of Space Competition

This is our reference implementation for the Proof of Space competition.

### Overview

The Proof of Space program is split into two parts -
- A generator which creates a plot given a value for k
- A prover which accesses the plot given a challenge

During this competition we will act as the verifier with a series of predetermined challenges.
There are 3 tracks to enter into. The winner of each track will need to pass each of the challenges and optimise for one of the following:

1. Fastest to generate the legal plot file without breaking any of the requirements
2. Least disk space used for generation
3. Smallest plot size after generation

### About Proofs of Space

We have included a document outlining the constructions for the Proof of Space system, as well as a document explaining our reference implementation.
It is highly recommended that you read these documents.

It is also recommended that you read the [Beyond Hellman's Time-Memory Trade-Offs](https://eprint.iacr.org/2017/893.pdf) paper.

Finally, to understand more of the applications of this system, you can read about the [Chia Consensus Algorithm](https://www.chia.net/assets/ChiaGreenPaper.pdf).

### Further Details

Entrants will have access to our Keybase bot which allows for testing before final submission.
Keybase tests will use k=23 to ensure the machines are not tied up for too long.
The final submissions will be evaluated with k=30 and a time limit of 24 hours on the judging machine, so it is recommended that entrants test larger k values on their local machines.

All entries will be tested on a standardised machine.
The test hardware has a Xeon W-2123 CPU, a RTX 2080 GPU, a 1TB WD Blue HDD and 8GB of RAM.
Each entry will run on a clean install of Ubuntu 18.10.

Submissions and tests through Keybase should include the following files:

- install.sh - which compiles the source code and installs dependencies
- generate.sh - file which takes a value of k and a plot seed and generates a plot file in the local directory
- prove.sh - which takes a challenge and returns a proof

The non-final Keybase tests will use a small value for k for the plot generation, but the final evaluation will use a large value.

The final judging precommitment for the plot ID(seed) and challenges is 315e54e4734145dca0d715a59bbc0281cd73e05985a870a987a31b313365d882.

Final submissions should all be done through Keybase.

The implementations should find all proofs of space that the reference implementation in "src/cpp" finds.
The Hellman example is just provided for guidence, but will not be used for judging.

### How To Enter

An Entry may be submitted by a team of individuals working collaboratively (a “Team Contestant”).
In this case, each individual member of the team must complete the Entry Form and all members of the Team Contestant must designate the same point of contact to receive official Challenge correspondence.

To enter send a completed Entry Form to [hello@chia.net](mailto:hello@chia.net)


For other questions you can join our public Keybase channel [here](https://keybase.io/team/chia_network.public).
