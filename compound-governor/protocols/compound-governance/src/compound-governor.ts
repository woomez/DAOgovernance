import { Address } from "@graphprotocol/graph-ts";
import {
  ProposalCanceled,
  ProposalCreated,
  ProposalExecuted,
  ProposalQueued,
  VoteCast,
} from "../../../generated/COMPOUNDGovernor/COMPOUNDGovernor";
import {
  _handleProposalCreated,
  _handleProposalCanceled,
  _handleProposalExecuted,
  _handleProposalQueued,
  _handleVoteCast,
  getOrCreateProposal,
  getGovernance,
} from "../../../src/handlers";
import { COMPOUNDGovernor } from "../../../generated/COMPOUNDGovernor/COMPOUNDGovernor";
import { Proposal } from "../../../generated/schema";
import {
  BIGINT_ONE,
  ProposalState,
} from "../../../src/constants";

// ProposalCanceled(proposalId)
export function handleProposalCanceled(event: ProposalCanceled): void {
  _handleProposalCanceled(event.params.id.toString(), event);
}

// ProposalCreated(proposalId, proposer, targets, values, signatures, calldatas, startBlock, endBlock, description)
// FIXME quorum values
export function handleProposalCreated(event: ProposalCreated): void {

  // FIXME: Prefer to use a single object arg for params
  // e.g.  { proposalId: event.params.proposalId, proposer: event.params.proposer, ...}
  // but graph wasm compilation breaks for unknown reasons
  _handleProposalCreated(
    event.params.id.toString(),
    event.params.proposer.toHexString(),
    event.params.targets,
    event.params.values,
    event.params.signatures,
    event.params.calldatas,
    event.params.startBlock,
    event.params.endBlock,
    event.params.description,
    event
  );
}

// ProposalExecuted(proposalId)
export function handleProposalExecuted(event: ProposalExecuted): void {
  _handleProposalExecuted(event.params.id.toString(), event);
}

// ProposalQueued(proposalId, eta)
export function handleProposalQueued(event: ProposalQueued): void {
  _handleProposalQueued(event.params.id, event.params.eta);
}

function getLatestProposalValues(
  proposalId: string,
  contractAddress: Address
): Proposal {
  let proposal = getOrCreateProposal(proposalId);

  // On first vote, set state and quorum values
  if (proposal.state == ProposalState.PENDING) {
    let contract = COMPOUNDGovernor.bind(contractAddress);
    proposal.state = ProposalState.ACTIVE;

    let governance = getGovernance();
    proposal.tokenHoldersAtStart = governance.currentTokenHolders;
    proposal.delegatesAtStart = governance.currentDelegates;
  }
  return proposal;
}

// VoteCast(account, proposalId, support, weight, reason);
export function handleVoteCast(event: VoteCast): void {
  let proposal = getLatestProposalValues(
    event.params.proposalId.toString(),
    event.address
  );

  // Proposal will be updated as part of handler
  _handleVoteCast(
    proposal,
    event.params.voter.toHexString(),
    event.params.votes,
    event.params.reason,
    event.params.support,
    event
  );
}

// Helper function that imports and binds the contract
// function getGovernanceFramework(contractAddress: string): GovernanceFramework {
//   let governanceFramework = GovernanceFramework.load(contractAddress);
// 
//   if (!governanceFramework) {
//     governanceFramework = new GovernanceFramework(contractAddress);
//     let contract = COMPOUNDGovernor.bind(Address.fromString(contractAddress));
// 
//     governanceFramework.name = contract.name();
//     governanceFramework.type = GovernanceFrameworkType.COMPOUND_GOVERNOR;
//     governanceFramework.version = contract.version();
// 
//     governanceFramework.contractAddress = contractAddress;
//     governanceFramework.tokenAddress = contract.token().toHexString();
//     governanceFramework.timelockAddress = contract.timelock().toHexString();
// 
//     governanceFramework.votingDelay = contract.votingDelay();
//     governanceFramework.votingPeriod = contract.votingPeriod();
//     governanceFramework.proposalThreshold = contract.proposalThreshold();
//     
//   }
// 
//   return governanceFramework;
// }
