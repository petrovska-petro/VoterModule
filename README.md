# Voter Module

This repository contains the smart contract for the Module, which will allow to trigger specific chores around the voter multisig thru the multisig. Tasks carried in the module:

- Process expired locks with the pursue of ensure that all voting power is available for future props, not leaving any expiring locks unattended
- Claims auraBAL rewards and transfers reward to trops multisig
- Withdraws graviAURA (up to amount available) and locks all naked AURA

The module is capped on the methods which will be trigger on-chain, and who can execute the `performUpKeep` method which originally has being thought to be CL keepers and techops multisig as back-up. Ideally, will be carry over by the CL keepers given the logic within `checkUpKeep` whenever conditions are met.

# Testing

In your terminal:

```
brownie test -s
```