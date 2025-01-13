import "../setup/CompleteSiloSetup.spec";
import "../silo/unresolved.spec";
import "../simplifications/Oracle_quote_one_UNSAFE.spec";
import "../simplifications/SimplifiedGetCompoundInterestRateAndUpdate_SAFE.spec";
import "../simplifications/SiloMathLib_SAFE.spec";

methods {
    
}

definition ignoredMethod(method f) returns bool =
    f.selector == sig:PartialLiquidation.initialize(address, bytes).selector;

rule doesntAlwaysRevert(method f, env e)
    filtered { f -> !ignoredMethod(f) }
{
    SafeAssumptionsEnv_withInvariants(e);
    calldataarg args;
    f(e, args);
    satisfy true;
}

rule maxLiquidationNeverReverts(env e, address user)
{
    address colSiloBefore = siloConfig(e).borrowerCollateralSilo(e, user);
    require colSiloBefore == silo0 || colSiloBefore == silo1 || colSiloBefore == 0;
    SafeAssumptions_withInvariants(e, user);
    uint256 collateralToLiquidate; uint256 debtToRepay; bool sTokenRequired;
    collateralToLiquidate, debtToRepay, sTokenRequired = maxLiquidation@withrevert(e, user);
    assert !lastReverted;
}

