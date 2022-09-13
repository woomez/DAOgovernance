import { BigInt } from '@graphprotocol/graph-ts'

import {
    VoteCast as VoteCastEvent,
    NewImplementation as NewImplementationEvent,
    ProposalCreated as ProposalCreatedEvent
} from "../generated/GovernorBravoDelegator/GovernorBravoDelegator"
import { Proposal, Single_Vote, Voter, Implementation } from "../generated/schema"


export function handleProposalCreated(event: ProposalCreatedEvent): void{
    let Id = event.params.id; 
    let proposal = Proposal.load(Id.toString());
    if (proposal == null){
        proposal = new Proposal(Id.toString());
        proposal.blocktime = event.block.timestamp;
        proposal.forvotes = BigInt.fromI32(0);
        proposal.againstvotes = BigInt.fromI32(0);
    }
    proposal.save();
}

export function handleVoteCast(event: VoteCastEvent): void {
    let voterId = event.params.voter;
    let proposalId = event.params.proposalId;

    let vote = Single_Vote.load(proposalId.toHexString() + "-" + voterId.toHexString());
    let single_vote = event.params.votes;
    let svi32 = single_vote;
    if (vote == null){
        vote = new Single_Vote(proposalId.toHexString() + "-" + voterId.toHexString());
        vote.voter = voterId.toHexString();
        vote.single_vote = single_vote;
        vote.proposalID = event.params.proposalId.toString();
        vote.support = event.params.support;
    }
    vote.save();

    let proposal = Proposal.load(proposalId.toString());
    if (proposal == null){
        proposal = new Proposal(proposalId.toString());
        if (event.params.support == 0) {
            proposal.againstvotes = svi32;
        } else if (event.params.support == 1) {
            proposal.forvotes = svi32; 
        }
    }

    if (event.params.support == 0) {
        proposal.againstvotes = proposal.againstvotes + svi32;
    } else if (event.params.support == 1) {
        proposal.forvotes = proposal.forvotes + svi32; 
      }
    proposal.save();

    let voter = Voter.load(voterId.toHexString());
    if (voter == null){
        voter = new Voter(voterId.toHexString());
    }
    voter.save();
}

export function handleNewImplementation(event: NewImplementationEvent): void{
    let oldId = event.params.oldImplementation;
    let implementation = Implementation.load(oldId.toHexString());
    if (implementation == null){
        implementation = new Implementation(oldId.toHexString());
        implementation.newImplementation = event.params.newImplementation
        implementation.blocktime = event.block.timestamp
    }
    implementation.save();
}
