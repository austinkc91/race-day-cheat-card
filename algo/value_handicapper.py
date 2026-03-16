#!/usr/bin/env python3
"""
Value Handicapper Algorithm v1.0
Focus: Finding big-payout winners by identifying undervalued horses.

Strategy: Instead of picking favorites (chalk), this algorithm identifies horses
that have REAL chances but are being overlooked by the public. We combine:
1. Multi-source consensus (who do experts like?)
2. Value Score (consensus vs odds mismatch = opportunity)
3. Contrarian indicators (when everyone loves the favorite, look elsewhere)
4. Class/form analysis (class droppers, improving form)
5. Trainer/jockey power combos

The goal is NOT to pick the most likely winner. The goal is to find horses
where our estimated probability > the odds-implied probability. That's where
the money is.
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Horse:
    name: str
    pp: int  # post position
    ml_odds: str  # morning line odds as string like "7/2"
    jockey: str = ""
    trainer: str = ""
    # Source picks (True = picked by source)
    sftb_rank: Optional[float] = None  # SFTB expected score (lower = better)
    racing_dudes_pick: bool = False
    hrn_pick: bool = False
    ai_horse_picks_prob: Optional[float] = None  # win probability %
    allchalk_rank: Optional[int] = None
    ultimate_capper_pick: bool = False
    # Computed
    value_score: float = 0.0
    consensus_count: int = 0
    algo_score: float = 0.0
    bet_type: str = ""  # "WIN", "PLACE", "VALUE", "SKIP"


@dataclass
class Race:
    number: int
    track: str
    date: str
    race_type: str  # "Maiden Claiming", "Allowance", etc.
    distance: str
    surface: str  # "Dirt", "Turf"
    purse: int
    post_time: str = ""
    horses: list = field(default_factory=list)


def parse_odds_to_decimal(odds_str: str) -> float:
    """Convert odds string like '7/2' or '4/5' to decimal multiplier."""
    odds_str = odds_str.strip()
    if "/" in odds_str:
        num, den = odds_str.split("/")
        return float(num) / float(den)
    return float(odds_str)


def odds_to_implied_prob(odds_str: str) -> float:
    """Convert morning line odds to implied probability."""
    dec = parse_odds_to_decimal(odds_str)
    return 1.0 / (dec + 1.0)


def score_horse(horse: Horse, race: Race, field_size: int) -> None:
    """
    Score a horse using our value-focused algorithm.

    The key insight: We're not trying to find the BEST horse.
    We're trying to find horses whose REAL probability of winning
    is higher than what the odds suggest.
    """
    dec_odds = parse_odds_to_decimal(horse.ml_odds)
    implied_prob = odds_to_implied_prob(horse.ml_odds)

    # === CONSENSUS COUNT ===
    # Count how many sources like this horse
    consensus = 0

    # SFTB: rank 1 = top pick, rank <= 2 = strong
    if horse.sftb_rank is not None:
        if horse.sftb_rank <= 1.0:
            consensus += 1
        elif horse.sftb_rank <= 1.5:
            consensus += 0.5

    if horse.racing_dudes_pick:
        consensus += 1
    if horse.hrn_pick:
        consensus += 1
    if horse.ultimate_capper_pick:
        consensus += 1

    # AI Horse Picks: if win prob > 20%, that's a pick
    if horse.ai_horse_picks_prob is not None:
        if horse.ai_horse_picks_prob > 25:
            consensus += 1
        elif horse.ai_horse_picks_prob > 15:
            consensus += 0.5

    # AllChalk: rank 1 = top pick
    if horse.allchalk_rank is not None:
        if horse.allchalk_rank <= 1:
            consensus += 1
        elif horse.allchalk_rank <= 2:
            consensus += 0.5

    horse.consensus_count = int(consensus)

    # === VALUE SCORE ===
    # Value = consensus strength * odds multiplier
    # High consensus + high odds = HUGE value
    # High consensus + low odds = chalk (boring)
    max_sources = 6
    consensus_pct = consensus / max_sources

    # Value score: how much the odds exceed what consensus suggests
    # If 3/6 sources like a horse at 8/1, that's WAY more valuable
    # than 3/6 sources liking a horse at 6/5
    horse.value_score = consensus_pct * dec_odds

    # === ALGO SCORE (our proprietary rating) ===
    score = 0.0

    # 1. Base consensus score (0-30 points)
    score += consensus * 5

    # 2. Value multiplier (0-40 points)
    # This is the KEY differentiator - rewards horses with support at high odds
    if dec_odds >= 3.0:  # 3/1 or higher
        value_bonus = min(consensus_pct * dec_odds * 8, 40)
        score += value_bonus
    elif dec_odds >= 2.0:  # 2/1 to 3/1
        score += consensus_pct * dec_odds * 4
    else:  # Under 2/1 - chalk penalty
        score += consensus_pct * 3  # minimal credit

    # 3. AI model agreement bonus (0-15 points)
    if horse.ai_horse_picks_prob is not None:
        if horse.ai_horse_picks_prob > 20 and dec_odds >= 3.0:
            # AI thinks they have a real shot but odds are high = gold
            score += 15
        elif horse.ai_horse_picks_prob > 15 and dec_odds >= 4.0:
            score += 12
        elif horse.ai_horse_picks_prob > 10:
            score += 5

    # 4. SFTB algorithm agreement (0-10 points)
    if horse.sftb_rank is not None:
        if horse.sftb_rank <= 1.0:
            score += 10
        elif horse.sftb_rank <= 1.5:
            score += 7
        elif horse.sftb_rank <= 2.0:
            score += 4

    # 5. Class/race type modifier
    race_lower = race.race_type.lower()
    if "maiden" in race_lower and "claiming" in race_lower:
        # Maiden claiming - consensus picks are MORE reliable here (from backtest)
        score += consensus * 2
    elif "allowance" in race_lower or "stakes" in race_lower:
        # Higher class - form is more predictive
        score += consensus * 1.5
    # Low-level claiming - upsets galore, reduce confidence in chalk
    elif "claiming" in race_lower:
        if dec_odds <= 2.0:  # Chalk in cheap claiming = trap
            score -= 5
        if dec_odds >= 4.0 and consensus >= 2:  # But value picks in claiming = good
            score += 8

    # 6. Field size adjustment
    if field_size <= 5:
        # Small field - chalk more likely, reduce value premium
        score *= 0.8
    elif field_size >= 9:
        # Big field - more chaos, value plays have more room
        score *= 1.15

    # 7. Longshot bonus for horses with ANY expert support
    if dec_odds >= 6.0 and consensus >= 1.5:
        score += 10  # Expert-backed longshot bonus
    if dec_odds >= 10.0 and consensus >= 1:
        score += 8  # Huge odds with any support

    horse.algo_score = round(score, 1)

    # === BET RECOMMENDATION ===
    if horse.algo_score >= 35 and dec_odds >= 4.0:
        horse.bet_type = "VALUE WIN"  # Our bread and butter
    elif horse.algo_score >= 30 and dec_odds >= 3.0:
        horse.bet_type = "WIN"
    elif horse.algo_score >= 25:
        horse.bet_type = "PLACE"
    elif horse.algo_score >= 20 and dec_odds >= 6.0:
        horse.bet_type = "SAVER"  # Small bet on a live longshot
    else:
        horse.bet_type = "SKIP"


def analyze_race(race: Race) -> dict:
    """Analyze a single race and return structured results."""
    field_size = len(race.horses)

    for horse in race.horses:
        score_horse(horse, race, field_size)

    # Sort by algo score descending
    ranked = sorted(race.horses, key=lambda h: h.algo_score, reverse=True)

    # Find the best value play
    value_plays = [h for h in ranked if h.bet_type in ("VALUE WIN", "SAVER") and parse_odds_to_decimal(h.ml_odds) >= 4.0]
    top_picks = [h for h in ranked if h.bet_type != "SKIP"]

    return {
        "race": race,
        "ranked": ranked,
        "value_plays": value_plays,
        "top_picks": top_picks,
        "best_value": value_plays[0] if value_plays else None,
        "top_pick": ranked[0] if ranked else None,
    }


def format_race_analysis(analysis: dict) -> str:
    """Format race analysis as readable text."""
    race = analysis["race"]
    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"RACE {race.number} | {race.track} | {race.date}")
    lines.append(f"{race.race_type} | {race.distance} {race.surface} | ${race.purse:,} | {race.post_time}")
    lines.append(f"Field: {len(race.horses)} horses")
    lines.append(f"{'='*60}")

    lines.append(f"\n{'Horse':<25} {'ML':>6} {'Cons':>4} {'Value':>6} {'Score':>6} {'Action':>12}")
    lines.append("-" * 70)

    for h in analysis["ranked"]:
        action_marker = ""
        if h.bet_type == "VALUE WIN":
            action_marker = "*** VALUE ***"
        elif h.bet_type == "WIN":
            action_marker = ">> WIN <<"
        elif h.bet_type == "PLACE":
            action_marker = "PLACE"
        elif h.bet_type == "SAVER":
            action_marker = "$ SAVER $"

        lines.append(f"{h.name:<25} {h.ml_odds:>6} {h.consensus_count:>4} {h.value_score:>6.1f} {h.algo_score:>6.1f} {action_marker:>12}")

    if analysis["best_value"]:
        bv = analysis["best_value"]
        lines.append(f"\nBEST VALUE: {bv.name} at {bv.ml_odds} (Score: {bv.algo_score}, Value: {bv.value_score:.1f})")

    if analysis["top_pick"]:
        tp = analysis["top_pick"]
        lines.append(f"TOP PICK: {tp.name} at {tp.ml_odds} (Score: {tp.algo_score})")

    return "\n".join(lines)


def generate_betting_card(analyses: list) -> str:
    """Generate a complete betting card for a race day."""
    lines = []
    total_cost = 0
    bets = []

    lines.append("\n" + "=" * 60)
    lines.append("BETTING CARD - VALUE HUNTER STRATEGY")
    lines.append("=" * 60)
    lines.append("Focus: Big payouts via value plays and live longshots")
    lines.append("Default bet: $2 WIN on value plays, $2 PLACE on top picks\n")

    for a in analyses:
        race = a["race"]

        for h in a["ranked"]:
            if h.bet_type == "VALUE WIN":
                bet_amt = 3 if parse_odds_to_decimal(h.ml_odds) >= 6.0 else 2
                bets.append({
                    "race": race.number,
                    "horse": h.name,
                    "type": "WIN",
                    "amount": bet_amt,
                    "odds": h.ml_odds,
                    "reason": f"VALUE PLAY - Score {h.algo_score}, {h.consensus_count} sources at {h.ml_odds}",
                    "potential_win": round(bet_amt * parse_odds_to_decimal(h.ml_odds), 2)
                })
                # Also add place bet as insurance
                bets.append({
                    "race": race.number,
                    "horse": h.name,
                    "type": "PLACE",
                    "amount": 2,
                    "odds": h.ml_odds,
                    "reason": "Insurance on value play",
                    "potential_win": round(2 * parse_odds_to_decimal(h.ml_odds) * 0.4, 2)  # estimate
                })
                total_cost += bet_amt + 2
            elif h.bet_type == "WIN":
                bets.append({
                    "race": race.number,
                    "horse": h.name,
                    "type": "WIN",
                    "amount": 2,
                    "odds": h.ml_odds,
                    "reason": f"Strong score {h.algo_score}, {h.consensus_count} sources",
                    "potential_win": round(2 * parse_odds_to_decimal(h.ml_odds), 2)
                })
                total_cost += 2
            elif h.bet_type == "SAVER":
                bets.append({
                    "race": race.number,
                    "horse": h.name,
                    "type": "WIN",
                    "amount": 2,
                    "odds": h.ml_odds,
                    "reason": f"LONGSHOT SAVER - {h.consensus_count} sources at {h.ml_odds}",
                    "potential_win": round(2 * parse_odds_to_decimal(h.ml_odds), 2)
                })
                total_cost += 2

    for b in bets:
        marker = "***" if "VALUE" in b["reason"] or "LONGSHOT" in b["reason"] else ""
        lines.append(f"R{b['race']} | ${b['amount']} {b['type']:>5} | {b['horse']:<25} | {b['odds']:>6} | Pot. ${b['potential_win']:>7.2f} {marker}")

    lines.append(f"\nTOTAL COST: ${total_cost}")
    lines.append(f"TOTAL BETS: {len(bets)}")

    # Calculate potential ROI scenarios
    if bets:
        value_bets = [b for b in bets if "VALUE" in b["reason"] or "LONGSHOT" in b["reason"]]
        if value_bets:
            best_potential = max(b["potential_win"] for b in value_bets)
            lines.append(f"\nBIGGEST POTENTIAL WIN: ${best_potential:.2f} from a single $2-3 bet")
            total_potential = sum(b["potential_win"] for b in value_bets)
            lines.append(f"IF ALL VALUE PLAYS HIT: ${total_potential:.2f}")

    return "\n".join(lines)


if __name__ == "__main__":
    # This will be called with race data from our research
    print("Value Handicapper Algorithm v1.0")
    print("Run with race data to generate picks")
