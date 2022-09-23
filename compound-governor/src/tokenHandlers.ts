import { BigInt, log, ethereum } from "@graphprotocol/graph-ts";
import { BIGINT_ONE, BIGINT_ZERO, ZERO_ADDRESS } from "./constants";
import {
  getGovernance,
  getOrCreateDelegate,
  getOrCreateTokenHolder,
  createDelegation,
  getDelegation,
  toDecimal,
  getOrCreateTokenDailySnapshot,
} from "./handlers";
import {Delegation} from "../generated/schema";

export function _handleDelegateChanged(
  delegator: string,
  fromDelegate: string,
  toDelegate: string,
  event: ethereum.Event
): void {
 
  let tokenHolder = getOrCreateTokenHolder(delegator);
  let previousDelegate = getOrCreateDelegate(fromDelegate);
  let newDelegate = getOrCreateDelegate(toDelegate);
  let delegationId = event.block.number.toHexString().concat("-").concat(newDelegate.id);
  let delegation = createDelegation(delegationId, tokenHolder.id, newDelegate.id, event);

  tokenHolder.delegate = newDelegate.id;
  tokenHolder.save();

  previousDelegate.tokenHoldersRepresentedAmount =
    previousDelegate.tokenHoldersRepresentedAmount - 1;
  previousDelegate.save();

  newDelegate.tokenHoldersRepresentedAmount =
    newDelegate.tokenHoldersRepresentedAmount + 1;
  newDelegate.save();

  delegation.delegator = tokenHolder.id;
  delegation.delegate = newDelegate.id;
  delegation.delegatorTokens = tokenHolder.tokenBalance;
  delegation.delegateTokens = newDelegate.delegatedVotes;
  delegation.txnHash = event.transaction.hash.toHexString();
  delegation.save();
}

export function _handleDelegateVotesChanged(
  delegateAddress: string,
  previousBalance: BigInt,
  newBalance: BigInt,
  event: ethereum.Event
): void {
  let votesDifference = newBalance.minus(previousBalance);

  let delegate = getOrCreateDelegate(delegateAddress);
  let delegationId = event.block.number.toHexString().concat("-").concat(delegate.id);

  delegate.delegatedVotesRaw = newBalance;
  delegate.delegatedVotes = toDecimal(newBalance);
  delegate.save();


  // Update governance delegate count
  let governance = getGovernance();
  if (previousBalance == BIGINT_ZERO && newBalance > BIGINT_ZERO) {
    governance.currentDelegates = governance.currentDelegates.plus(BIGINT_ONE);
  }
  if (newBalance == BIGINT_ZERO) {
    governance.currentDelegates = governance.currentDelegates.minus(BIGINT_ONE);
  }
  governance.delegatedVotesRaw =
    governance.delegatedVotesRaw.plus(votesDifference);
  governance.delegatedVotes = toDecimal(governance.delegatedVotesRaw);
  governance.save();

  let delegation = getDelegation(delegationId, votesDifference);
  if (delegation){
    delegation.save();
  }

}

export function _handleTransfer(from: string, to: string, value: BigInt, event: ethereum.Event): void {
  let fromHolder = getOrCreateTokenHolder(from);
  let toHolder = getOrCreateTokenHolder(to);
  let governance = getGovernance();
  let isBurn = to == ZERO_ADDRESS;
  let isMint = from == ZERO_ADDRESS;

  if (!isMint) {
    let fromHolderPreviousBalance = fromHolder.tokenBalanceRaw;
    fromHolder.tokenBalanceRaw = fromHolder.tokenBalanceRaw.minus(value);
    fromHolder.tokenBalance = toDecimal(fromHolder.tokenBalanceRaw);

    if (fromHolder.tokenBalanceRaw < BIGINT_ZERO) {
      log.error("Negative balance on holder {} with balance {}", [
        fromHolder.id,
        fromHolder.tokenBalanceRaw.toString(),
      ]);
    }

    if (
      fromHolderPreviousBalance > BIGINT_ZERO &&
      fromHolder.tokenBalanceRaw == BIGINT_ZERO
    ) {
      governance.currentTokenHolders =
        governance.currentTokenHolders.minus(BIGINT_ONE);
      governance.save();
    }
    fromHolder.save();
  }

  // Increment to holder balance and total tokens ever held
  let toHolderPreviousBalance = toHolder.tokenBalanceRaw;
  toHolder.tokenBalanceRaw = toHolder.tokenBalanceRaw.plus(value);
  toHolder.tokenBalance = toDecimal(toHolder.tokenBalanceRaw);
  toHolder.totalTokensHeldRaw = toHolder.totalTokensHeldRaw.plus(value);
  toHolder.totalTokensHeld = toDecimal(toHolder.totalTokensHeldRaw);

  if (
    toHolderPreviousBalance == BIGINT_ZERO &&
    toHolder.tokenBalanceRaw > BIGINT_ZERO
  ) {
    governance.currentTokenHolders =
      governance.currentTokenHolders.plus(BIGINT_ONE);
    governance.save();
  }
  toHolder.save();

  // Adjust token total supply if it changes
  if (isMint) {
    governance.totalTokenSupply = governance.totalTokenSupply.plus(value);
    governance.save();
  } else if (isBurn) {
    governance.totalTokenSupply = governance.totalTokenSupply.minus(value);
    governance.save();
  }

  // Take snapshot
  let dailySnapshot = getOrCreateTokenDailySnapshot(event.block);
  dailySnapshot.totalSupply = governance.totalTokenSupply;
  dailySnapshot.tokenHolders = governance.currentTokenHolders;
  dailySnapshot.delegates = governance.currentDelegates;
  dailySnapshot.blockNumber = event.block.number;
  dailySnapshot.timestamp = event.block.timestamp;
  dailySnapshot.save();

}
