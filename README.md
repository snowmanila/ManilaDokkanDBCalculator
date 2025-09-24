# Manila's Dokkan DB Calculator

## Overview

Hello, and welcome to my **Dokkan Battle Calculator**! For those who are curious, this is a calculator for the `Dragon Ball Z: Dokkan Battle` mobile game, based on the Japanese series of the same name. In `Dokkan`, you collect characters from the series, build teams, and run them in various events, something like a mix between traditional RPGs and Pokemon. Each unit has their own kit and passives, giving them unique abilities and skills that aid them in battle. As the game reached its 10th year anniversary this year, you would imagine the game developers would add more and more things to the game to keep the energy going, right? This is very much true, and that goes for the characters you can obtain. While it's pretty fun observing new character releases and being hyped over the things they can do, it can be very tedious calculating the characters' passive skills, especially with how long and articulate they are getting, as well as the various cases you have to calculate for.

To save on this, I developed a Python script utilizing in-game information to calculate character kits, using character IDs and gathering information using Dokkan's official database files. The calculator works by using a GUI to get a character's ID number, and gathering the unit's kit using SQL queries. The GUI will then list out the character's stat buffs as checkboxes, allowing users to enable/disable parts of their kit. If a partner is also listed, the program will go through the partner's links and adds the multiplicative buff based on links shared. After applying Active, Domain and Ki multipler buffs, the 'on attack' buffs are added (if selected) before finally applying each Super Attack the character has. For those curious on the process, here are how Dokkan units are calculated:
    1. Base Attack (What is shown on the character's card screen)
    2. Multiply by Leader Skill Buff
        - ATK = int(ATK * ((1 + Leader1 + Leader2)/100)) (i.e. multiply by 5.40 for dual 220% leads)
    3. Multiply by SoT Percentage Buffs (i.e. ATK +100% = ATK * 2)
        - ATK = int(ATK * (1 + (atkPerBuff/100)))
    4. Add SoT Flat Buffs (i.e. ATK +100 = ATK + 100)
        - ATK = int(ATK + atkFlatBuff)
    5. Multiply by Link Buffs from Partner(s)
        - ATK = int(ATK * (1 + (totalLinkBuffs/100)))
    6. Multiply by Active Skill Buffs (if applicable) (Add buffs if multiple)
        - ATK = int(ATK * (1 + (activeBuff/100)))
    7. Multiply by Domain Skill Buffs (if applicable) (Add buffs if multiple)
        - ATK = int(ATK * (1 + (domainBuff/100)))
    8. **(ATK Only)** Multiply by Ki Multiplier (Varies by Unit, changes with the amount of Ki the character has)
        - **(For Units that cannot go past 12 Ki):** kiMultiplier = (12KiMultiplier/24)*(12+kiValue)
        - **(For > 12 Ki (LRs))**: kiMultiplier = (((200-12KiMultiplier)/12)*(characterKi-12))+12KiMultiplier
        - ATKnew = int(ATK * (kiMultiplier/100))
    9. Multiply by 'On Attack' Percentage Buffs
        - ATK = int(ATK * (1 + (saPerBuff/100)))
        - **'On Attack' refers to passives that are activated when the character is attacking. Passives include 'When attacking', 'For every Ki when attacking', 'When the target enemy...', 'When the Finish Effect is activated', etc.**
            - **Does not apply to 'As the x attacker in a turn', which is calculated with initial calcs**
            - Only add Finish Effect stat when calculating for Finish Effect APT
    10. Add 'On Attack' Flat Buffs
        - ATK = int(ATK + saFlatBuff)
    11. Apply SA Effects (if applicable):
        - **(ATK Only)** Multiply by (ATK Multiplier + SA Multiplier + SA Bonus Buffs (if applicable) (Super Attack Power +x%))
            - For additional/stacking Super Attacks, add ATK multiplier for each Super Attack performed
        - **(DEF Only)** Multiply by (1 + DEF Multiplier)
        - For additional/stacking Super Attacks, add ATK/DEF multiplier for each Super Attack performed, then multiply

    For Active Skills:
        - Calculate until Step 7, exclude nuking 'on attack' passives and other 'on attack' passives that Active Skills won't activate.
        - Multiply by ATK raise from Active Skill (if applicable)
            - Continue normal calculation if calculating SA ATK with Active buff
        - Multiply by damage multiplier (and stacks if applicable) if calculating Active Skill APT (if applicable)

    For Finish Skills:
        - Calculate until Step 7, exclude nuking 'on attack' passives and other 'on attack' passives that Active Skills won't activate.
        - Add Finish Skill passive to 'on attack' passive buff calculation
        - If charge-based:
            - Multiply by (ATK raise from Standby Skill (if applicable) + Finish Skill Multiplier (+ stacks if applicable))
            - ATK raise = Charge count * ATK raise per charge (If charge-based)
        - If KO:
            - Multiply by (ATK raise from SA (if applicable) + Finish Skill Multiplier (+ stacks if applicable))
        - Multiply by damage multiplier (and stacks if applicable) if calculating Active Skill APT (if applicable)

This should cover everything used in the stat calculation process.

This calculator is currently a WIP, with different cases and passives still being tested with each unit. So consider this an open-beta test for the Calculator! This calculator has already been tested for a bulk number of units, considering HiPo, EZAs, and other factors, as well as all links and calculating link buffs from partners. If there are any issues with the calculator, or any questions or suggestions, feel free to reach out!

Anyways, I hope everyone enjoys this (early-access) version of the Dokkan Calculator!

- Manila ❤
