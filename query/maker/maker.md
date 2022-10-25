== Understanding Maker ==
Q. What is the difference between executive and spell?
    Q. What does it mean for a spell to be casted/lifted?
    Q. What does it mean to add/delete/lock/free action to a spell?
    Q. Where does type of action come from?
    Q. What is slate?
    Q. What is an 'interface' for the VotingAction?
    
    S. Find one spell, look through example


== Subgraph == 
Q. Does the current subgraph for Maker provide weights for executive votes?

    Q. What information can be retrieved from the timeline?


== MISC ==
Q. What are the current limitations for generating CSVs for Maker?

    Q. What am I able to generate from the API if so?

## Governance Polls
    - Determine governance and DAO processes outside the technical layer of the Maker Protocol.

# Use case:
    - Form consensus on important community goals and targets.
    - Measure sentiment on potential Executive Vote proposals.
    - Ratify governance proposals originating from the MakerDAO forum signal threads.
    - Determine which values certain system parameters should be set to before those values are then confirmed in an executive vote.
    - Ratify risk parameters for new collateral types as presented by Risk Teams.

# Misc:
    - Current schedule calls for polls to 'go live' on a weekly basis every Monday at 12pm EST/9am PST/14:00 UTC.
    - Recurring polls of the same type are usually standardized and have the same duration. The most common are three and seven day periods.
    - Currently, only the elected Governance Facilitator(s) are able to put up polls that display on the Governance Portal

## Executive Votes

    These also occur on-chain and can be accessed through the Maker Foundation's Voting Portal. Executive Votes "execute" technical changes to the Maker Protocol. When active, each Executive Vote has a proposed set of changes being made on the Maker Protocol's smart-contracts. Unlike the other types of votes, Executive Votes use a 'Continuous Approval Voting' model.

    Executive Votes can be used to:
    Add or remove collateral types.
    Add or remove Vault types.
    Adjust global system parameters.
    Adjust Vault-specific parameters.
    Replace modular smart contracts.
    
# Misc:
    - Current schedule calls for Executive Votes to go live on Fridays 12pm EST/9am PST/14:00 UTC

    
## Voting Contract:
    - To vote, MKR owners must "lock-up" tokens by transferring them into the Voting Contract. "Locked" MKR can be withdrawn at any time.
    - Executive Votes can receive votes at any time unless they were pre-coded with an expiration time. Governance Polls are time-based and can receive votes at any point before they expire.

