import ast
import math
import os
import sqlite3
import time # Time used for debugging
import tkinter as tk
import urllib.request

from dataclasses import dataclass, field
from PIL import Image, ImageTk
from tkinter import *
from tkinter import scrolledtext
        
# Written by snowmanila/manilamania (Updated: 9/22/25)
        
# Class for keeping track of a unit and its kit
@dataclass
class Unit:
    id: int
    name: str
    rarity: str # N, R, SR, SSR, UR, LR
    hp_max: int # Max stat without HiPo
    atk_max: int
    def_max: int
    # Elements in order: AGL, TEQ, INT, STR, PHY (0-4)
    # Super AGL, TEQ, INT, STR, PHY (10-14)
    # Extreme AGL, TEQ, INT, STR, PHY (20-24)
    awakening_element_type: str # Super, Extreme
    element: str # AGL, TEQ, INT, STR, PHY
    skill_lv_max: int
    eball_mod_mid: int # Should be 0 for non-LRs
    eball_mod_mid_num: int # Should be 0 for non-LRs
    eball_mod_max: int
    eball_mod_max_num: int
    leader_skill: str
    passive_skill_set_id: int
    active_skill_set_id: int
    categories: list
    specials: list
    transformation: int
    costumes: list
    optimal_awakening_growths: list
    card_links: list
    finish_skills: list
    standby_skills: list
    dokkan_fields: list
    
    def __init__(self, id, name, rarity, hp_max, atk_max, def_max, awakening_element_type,
    element, skill_lv_max, eball_mod_mid, eball_mod_mid_num, eball_mod_max, eball_mod_max_num,
    leader_skill, passive_skill_set_id, active_skill_set_id, categories, specials,
    transformation, costumes, optimal_awakening_growths, card_links, finish_skills,
    standby_skills, dokkan_fields):
        self.id = id
        self.name = name
        self.rarity = rarity
        self.hp_max = hp_max
        self.atk_max = atk_max
        self.def_max = def_max
        self.awakening_element_type = awakening_element_type
        self.element = element
        self.skill_lv_max = skill_lv_max
        self.eball_mod_mid = eball_mod_mid
        self.eball_mod_mid_num = eball_mod_mid_num
        self.eball_mod_max = eball_mod_max
        self.eball_mod_max_num = eball_mod_max_num
        self.leader_skill = leader_skill
        self.passive_skill_set_id = passive_skill_set_id
        self.active_skill_set_id = active_skill_set_id
        self.categories = categories
        self.specials = specials
        self.transformation = transformation
        self.costumes = costumes
        self.optimal_awakening_growths = optimal_awakening_growths
        self.card_links = card_links
        self.finish_skills = finish_skills
        self.standby_skills = standby_skills
        self.dokkan_fields = dokkan_fields
        
# Class for keeping track of a linking partner
@dataclass
class Partner:
    id: int
    name: str
    rarity: str
    element2: str
    card_links: list
    
    def __init__(self, id, name, rarity, element, card_links):
        self.id = id
        self.name = name
        self.rarity = rarity
        self.element = element
        self.card_links = card_links

# To-Do: Ask for main character ID in terminal, then create window to list character info and select options:
# 1. Print character info
# 2. Add tabs for selecting passives + partner + EZAs/HiPo

# Units that do not fit in terminal:
# - SEZA LR INT SSJ2 Gohan
# - EZA UR PHY Future Android #17
# - EZA UR TEQ Android #18

# Dev Note: Adjust stacking patterns between:
# Units with multiple SAs + multiple stacking patterns (STR Perfect Cell)
# Units with perm + temp raises (TEQ LR Dragon Fist EZA)
# Units with stacking base + temp transformed forms (TEQ Ultimate Gohan?)
# Units with temp base + stacking transformed forms (AGL Turles)
# Units with stacking base + transformed forms (INT UI Goku)

# Dev Note: Adjust AGL LR Gotenks
# Dev Note: Adjust TEQ LR Broly's EZA stacks (Multi-select?)

# Dev Note: Adjust stacking quantities in calculation, refer to additional documentation

# Calculate ATK stat given 'on attack' conditions (When attacking, per attack
# evaded/received/performed, when the target enemy ..., etc.)
# Dev Note: Adjust for multiple stat buffs with one SA (PHY Gorilla)
def calcStatAttack(characterKit, dbCursor, special, newStat, onAttackStat, atkBuff, defBuff, counter, crit, superEffective, additional):       
    dbCursor.execute(f'''SELECT * FROM specials WHERE special_set_id = {special[0]} AND 
    (target_type = 1 or target_type = 2 or target_type = 12 or target_type = 13)''')
    dbOutput = dbCursor.fetchall()
    if dbOutput:
        for specialPart in dbOutput:
            match specialPart[3]:
                case 1 | 3:
                    if special[0] == characterKit.specials[0][0]:
                        for turn in range(1, (specialPart[6]*additional)+2):
                            print(f'Super Attack {turn}: Raises ATK by {specialPart[9]*turn}%')
                            calcATKSA(characterKit, dbCursor, special, newStat, counter, crit, superEffective, additional, specialPart[9]*turn)
                    else:
                        for turn in range(1, specialPart[6]+1):
                            calcATKSA(characterKit, dbCursor, special, newStat, counter, crit, superEffective, additional, specialPart[9]*turn)
                case _:
                    calcATKSA(characterKit, dbCursor, special, newStat, counter, crit, superEffective, additional, 0)
    else:
        calcATKSA(characterKit, dbCursor, special, newStat, counter, crit, superEffective, additional, 0)
        
    '''if onAttackStat[2]:
    match onAttackStat[2][0][4]:
        case 0: defBuff[1] += onAttackStat[2][0][12]
        case 1: defBuff[1] -= onAttackStat[2][0][12]  
        case 2: defBuff[0] += onAttackStat[2][0][12]
        case 3: defBuff[0] -= onAttackStat[2][0][12]
    onAttackStat[2].pop(0)
    calcStatAttack(characterKit, dbCursor, special, totalStat, onAttackStat, atkBuff, defBuff, counter, crit, superEffective, additional)''' 
    print()
    
def calcATKSA(characterKit, dbCursor, special, totalStat, counter, crit, superEffective, additional, atkMultiplier):    
    # SA multiplier
    dbCursor.execute(f'''SELECT * FROM special_sets where id = {special[0]}''')
    dbOutput = dbCursor.fetchall()
    saMultiplier = 100+dbOutput[0][5]+(dbOutput[0][6]*(characterKit.skill_lv_max-1))
    
    # Base SA multiplier (For additionals)
    dbCursor.execute(f'''SELECT * FROM special_sets where id = {characterKit.specials[0][0]}''')
    dbOutput = dbCursor.fetchall()
    baseMultiplier = 100+dbOutput[0][5]+(dbOutput[0][6]*(characterKit.skill_lv_max-1))
            
    # Adds HiPo SA boost for SSR/UR/LR characters
    if characterKit.rarity == 'UR' or characterKit.rarity == 'LR':
        saMultiplier += 75
        baseMultiplier += 75
        
    dbCursor.execute(f'''SELECT * FROM card_specials WHERE special_set_id = {special[0]}''')
    dbOutput = dbCursor.fetchall()
    dbCursor.execute(f'''SELECT * FROM special_bonuses WHERE id = {dbOutput[0][9]}''')
    bonus1 = dbCursor.fetchall()
    dbCursor.execute(f'''SELECT * FROM special_bonuses WHERE id = {dbOutput[0][12]}''')
    bonus2 = dbCursor.fetchall()
    if bonus1:
        match bonus1[0][3]:
            case 1 | 5: saMultiplier += bonus1[0][9]
        #    case 2:
        #        
        #    case 3:
        #        
        #    case 63:
    if bonus2:
        match bonus2[0][3]:
            case 1 | 5: saMultiplier += bonus2[0][9]
        #    case 2:
        #        
        #    case 3:
        #        
        #    case 63:
        
    dbCursor.execute(f'''SELECT * FROM card_specials WHERE special_set_id = {characterKit.specials[0][0]}''')
    dbOutput = dbCursor.fetchall()
    
    if dbOutput[0][9]:
        dbCursor.execute(f'''SELECT * FROM special_bonuses WHERE id = {dbOutput[0][9]}''')
        bonusOutput1 = dbCursor.fetchall()
        if bonusOutput1[0][12] == 100:
            saMultiplier += bonusOutput1[0][9]
    if dbOutput[0][12]:
        dbCursor.execute(f'''SELECT * FROM special_bonuses WHERE id = {dbOutput[0][12]}''')
        bonusOutput2 = dbCursor.fetchall()
        if bonusOutput2[0][12] == 100:
            saMultiplier += bonusOutput1[0][12]
    
    if characterKit.active_skill_set_id:
        dbCursor.execute(f'''SELECT * FROM active_skill_sets WHERE id = {characterKit.active_skill_set_id}''')
        activeOutput = dbCursor.fetchall()
        if activeOutput[0][7]:
            dbCursor.execute(f'''SELECT * FROM ultimate_specials WHERE id = {activeOutput[0][7]}''')
            ultimateMutiplier = dbCursor.fetchall()[0][3]
            if characterKit.id == 1016571:
                if input("Use JP Active Multiplier? (y/n): ") == 'y':
                    ultimateMutiplier = 550
            ultimateATK = int(totalStat[0]*(ultimateMutiplier/100))
            if crit:
                print(f'Active Skill APT ({ultimateMutiplier}%): {ultimateATK} (Crit: {int(ultimateATK*1.9)})')
            elif superEffective:
                print(f'Active Skill APT ({ultimateMutiplier}%): {ultimateATK} (Super Effective: {int(ultimateATK*1.5)})')
            else:
                print(f'Active Skill APT ({ultimateMutiplier}%): {ultimateATK}')

    finalATK = int(totalStat[0]*((saMultiplier+atkMultiplier)/100))
    if crit:
        print(f'Super Attack APT ({saMultiplier}%): {finalATK} (Crit: {int(finalATK*1.9)})')
    elif superEffective:
        print(f'Super Attack APT ({saMultiplier}%): {finalATK} (Super Effective: {int(finalATK*1.5)})')
    else:
        print(f'Super Attack APT ({saMultiplier}%): {finalATK}')
    
    if not (characterKit.specials[0][0] == special[0]):
        dbCursor.execute(f'''SELECT * FROM card_specials WHERE special_set_id = {characterKit.specials[0][0]}''')
        ki = dbCursor.fetchall()[0][6]
        dbCursor.execute(f'''SELECT * FROM specials WHERE special_set_id = {characterKit.specials[0][0]} AND 
        (target_type = 1 or target_type = 2 or target_type = 12 or target_type = 13)''')
        specialPart = dbCursor.fetchall()
        if specialPart:
            for turn in range(1, (specialPart[0][6]*additional)+1):
                finalATK = int(totalStat[0]*((baseMultiplier+atkMultiplier+(specialPart[0][9]*turn))/100))
                print(f'Additional Super Attack {turn} ({ki} Ki): {finalATK}')
    
    if counter:
        if crit:
            print(f'Counter APT (Before SA, {counter}%): {int(totalStat[0]*counter)} (Crit: {int(totalStat[0]*(counter/100)*1.9)})')     
            for i in range(1, additional+2):
                print(f'Counter APT (After SA {i}, {counter}%): {int(totalStat[0]*((counter+(atkMultiplier*i))/100))} (Crit: {int(totalStat[0]*((counter+(atkMultiplier*i))/100)*1.9)})')
        elif superEffective:
            print(f'Counter APT (Before SA, {counter}%): {int(totalStat[0]*(counter/100))} (Super Effective: {int(totalStat[0]*(counter/100)*1.5)})')     
            for i in range(1, additional+2):
                print(f'Counter APT (After SA {i}, {counter}%): {int(totalStat[0]*((counter+(atkMultiplier*i))/100))} (Super Effective: {int(totalStat[0]*((counter+(atkMultiplier*i))/100)*1.5)})')
        else:
            print(f"Counter APT (Before SA, {counter}%): {int(totalStat[0]*(counter/100))}")
            for i in range(1, additional+2):
                print(f"Counter APT (After SA {i}, {counter}%): {int(totalStat[0]*((counter+(atkMultiplier*i))/100))}")
                    
        '''if characterKit.finish_skills:
            # Removing buffs then recalculating with finish skill passive buff
            # 'When the Finish Effect is activated'
            ATK -= saFlatBuff
            ATK /= (1 + (saPerBuff/100))
            
            atkBuff = characterKit.finish_skills[len(characterKit.finish_skills)-1].split('+')[1]
            if atkBuff.__contains__('%'):
                saPerBuff += int(atkBuff.split('%')[0])
            else:
                saFlatBuff += int(atkBuff.split(' ')[0])
            
            ATK = int(ATK * (1 + (saPerBuff/100))) # Apply 'on attack' percentage buffs
            print(f"{ATK} (With {saPerBuff}% Finish Skill Buff)")
            ATK = int(ATK + saFlatBuff) # Apply 'on attack' flat buffs
            print(f"{ATK} (With {saFlatBuff} Flat Finish Skill Buff)")
            
            for finish_skill in characterKit.finish_skills[:-1]:
                finishMultiplier = 4 # Ferocious multiplier by default
                if characterKit.finish_skills[1].__contains__('super-intense damage'):
                    finishMultiplier = 5
                elif characterKit.finish_skills[1].__contains__('ultimate damage'):
                    finishMultiplier = 5.5
                elif characterKit.finish_skills[1].__contains__('super-ultimate damage'):
                    finishMultiplier = 7.5
                
                for i in range(0, turnLimit):
                    if i == 0:
                        if crit:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*finishMultiplier))} (Crit: {str(int(ATK*finishMultiplier*1.9))})")
                        elif superEffective:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*finishMultiplier))} (Super Effective: {str(int(ATK*finishMultiplier*1.9))})")
                        else:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*finishMultiplier))}")
                    else:
                        if crit:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*(1+ATKmultiplier+(baseATKmultiplier*i))*finishMultiplier))} (Crit: {str(int(ATK*(1+ATKmultiplier+(baseATKmultiplier*i))*finishMultiplier*1.9))})")
                        elif superEffective:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*(1+ATKmultiplier+(baseATKmultiplier*i))*finishMultiplier))} (Super Effective: {str(int(ATK*(1+ATKmultiplier+(baseATKmultiplier*i))*finishMultiplier*1.5))})")
                        else:
                            print(f"Finish Effect APT (With {i} Super Attack, {finishMultiplier*100}%): {str(int(ATK*(1+ATKmultiplier+(baseATKmultiplier*i))*finishMultiplier))}")'''

def checkCond2(characterKit, special, totalBuff, onAttackStat, crit, superEffective, additional):
    atkPerBuff = 0
    defPerBuff = 0
    atkFlatBuff = 0
    defFlatBuff = 0
    """Collects the names of all checked items."""
    '''checked_items = []
    for i, var in enumerate(atkdefVars2):
        #if var.get() == 1:
            # onAttackATK += onAttackStat[0][i][1]
            # onAttackDEF += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[0][i])
    for i, var in enumerate(atkVars2):
        #if var.get() == 1:
            # onAttackATK += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[1][i])
    for i, var in enumerate(defVars2):
        #if var.get() == 1:
            # onAttackDEF += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[2][i])'''
    
    newBuff = [int(totalBuff[0] * (1 + (atkPerBuff/100))), int(totalBuff[1] * (1 + (defPerBuff/100)))] # Apply 'on attack' percentage buffs
    print(f"| {newBuff[0]} | {newBuff[1]} | (With {atkPerBuff}%/{defPerBuff}% 'On Attack' Passive Buff)")
    newBuff[0] += int(atkFlatBuff) # Apply 'on attack' percent buffs
    newBuff[1] += int(defFlatBuff) # Apply 'on attack' flat buffs
    print(f"| {newBuff[0]} | {newBuff[1]} | (With {atkFlatBuff}/{defFlatBuff} Flat 'On Attack' Passive Buff)")
    
    calcStatAttack(characterKit, dbCursor, special, newBuff, onAttackStat, [0, 0], [0, 0], "", crit, superEffective, additional)

def calcStatKi(characterKit, totalBuff, onAttackStat, crit, superEffective, additional):
    if characterKit.specials:
        baseKiMultiplier = (((200-characterKit.eball_mod_mid)/12)*(characterKit.specials[0][2]-12))+characterKit.eball_mod_mid
        # Adjusts base Ki Multiplier for URs
        if characterKit.rarity == 'UR':
            baseKiMultiplier = (characterKit.eball_mod_max/24)*(12+characterKit.specials[0][2])
        baseATK = int(totalBuff[0] * (baseKiMultiplier/100)) # Apply base Ki multiplier
        
        for special in characterKit.specials:
            dbCursor.execute(f'''SELECT * FROM card_specials where id = {special[0]}''')
            dbOutput = dbCursor.fetchall()
            kiMultiplier = (((200-characterKit.eball_mod_mid)/12)*(special[1]-12))+characterKit.eball_mod_mid
            if special[2] == 12:
                if characterKit.rarity != 'LR':
                    kiMultiplier = characterKit.eball_mod_max
                else:
                    kiMultiplier = characterKit.eball_mod_mid
            elif special[2] < 12 and characterKit.rarity != 'LR':
                # (max ki multi - 1)/ki needed to reach 12ki from not being in negative ki multi*the ki obtained
                # for example, to find Gotenks 11ki its (1.4-1)/9*8
                # - u/kariru2, Reddit
                kiMultiplier = (characterKit.eball_mod_max/24)*(12+special[1])
            newBuff = [int(totalBuff[0] * (kiMultiplier/100)), totalBuff[1]] # Apply Ki multiplier
            print(f'| {newBuff[0]} | {newBuff[1]} | (With {kiMultiplier}% Ki Multiplier)')
            
            dbCursor.execute(f'''SELECT * FROM special_sets where id = {special[0]}''')
            saOutput = dbCursor.fetchall()
            print(f"Launching Super Attack: {saOutput[0][1]} at {special[1]} Ki")
            checkCond2(characterKit, special, newBuff, onAttackStat, crit, superEffective, additional)
        if special[1] < 12 and characterKit.rarity != 'LR':
            kiATK = int(ATK * (characterKit.eball_mod_max/100)) # Apply Ki multiplier
            print(f'{kiATK} (With {characterKit.eball_mod_max}% Ki Multiplier)')
            print(f"Launching Super Attack: {saOutput[0][1]} at 12 Ki")
            checkCond2(characterKit, special, newBuff, onAttackStat, crit, superEffective, additional)
        if special[1] < 18 and characterKit.rarity == 'LR':
            kiMultiplier = (((200-characterKit.eball_mod_mid)/12)*(18-12))+characterKit.eball_mod_mid
            kiATK = int(ATK * (kiMultiplier/100)) # Apply Ki multiplier
            print(f'{kiATK} (With {kiMultiplier}% Ki Multiplier)')
            print(f"Launching Super Attack: {saOutput[0][1]} at 18 Ki")
            checkCond2(characterKit, special, newBuff, onAttackStat, crit, superEffective, additional)
        if characterKit.rarity == "LR":
            newBuff = [int(totalBuff[0] * 2), totalBuff[1]]
            print(f'| {newBuff[0]} | {newBuff[1]} | (With 200% Ki Multiplier)')
            print(f"Launching Super Attack: {saOutput[0][1]} at 24 Ki")
            checkCond2(characterKit, special, newBuff, onAttackStat, crit, superEffective, additional)
    else:
        if characterKit.finish_skills:
            print("No Super Attacks found")
            saPerBuff = 0
            saFlatBuff = 0
            atkBuff = characterKit.finish_skills[len(characterKit.finish_skills)-1].split('+')[1]
            if atkBuff.__contains__('%'):
                saPerBuff += int(atkBuff.split('%')[0])
            else:
                saFlatBuff += int(atkBuff.split(' ')[0])
            
            if characterKit.rarity == "LR":
                kiATK = int(ATK * 2) # Apply Ki multiplier
                print(f'{kiATK} (With 200% Ki Multiplier)')
            else:
                print(characterKit.eball_mod_max)
                kiATK = int(ATK * (characterKit.eball_mod_max/100)) # Apply Ki multiplier
                print(f'{kiATK} (With {characterKit.eball_mod_max}% Ki Multiplier)')
            
            ATK = int(ATK * (1 + (saPerBuff/100))) # Apply 'on attack' percentage buffs
            print(f"{ATK} (With {saPerBuff}% 'On Attack' Passive Buff)")
            ATK = int(ATK + saFlatBuff) # Apply 'on attack' flat buffs
            print(f"{ATK} (With {saFlatBuff} Flat 'On Attack' Passive Buff)")
            
            for finish_skill in characterKit.finish_skills[:-1]:
                finishMultiplier = 4 # Ferocious multiplier by default
                if characterKit.finish_skills[1].__contains__('super-intense damage'):
                    finishMultiplier = 5
                elif characterKit.finish_skills[1].__contains__('ultimate damage'):
                    finishMultiplier = 5.5
                elif characterKit.finish_skills[1].__contains__('super-ultimate damage'):
                    finishMultiplier = 7.5
                
                charge = 1
                if finish_skill[1].__contains__('charge count'):
                    atkBuff = finish_skill[1].split('by ')[1]
                    for i in range(0, 160, 10):
                        charge += ((int(atkBuff.split('%')[0])*i)/100)
                        if crit:
                            print(f"Finish Effect APT (With {i} Charge, {finishMultiplier}%): {str(int(ATK*charge*finishMultiplier))} (Crit: {str(int(ATK*charge*finishMultiplier*1.9))})")
                        elif superEffective:
                            print(f"Finish Effect APT (With {i} Charge, {finishMultiplier}%): {str(int(ATK*charge*finishMultiplier))} (Super Effective: {str(int(ATK*charge*finishMultiplier*1.5))})")
                        else:
                            print(f"Finish Effect APT (With {i} Charge, {finishMultiplier}%): {str(int(ATK*charge*finishMultiplier))}")
                else:
                    if crit:
                        print(f"Finish Effect APT ({finishMultiplier*100}%): {str(int(ATK*charge*finishMultiplier))} (Crit: {str(int(ATK*charge*finishMultiplier*1.9))})")
                    elif superEffective:
                        print(f"Finish Effect APT ({finishMultiplier*100}%): {str(int(ATK*charge*finishMultiplier))} (Super Effective: {str(int(ATK*charge*finishMultiplier*1.5))})")
                    else:
                        print(f"Finish Effect APT ({finishMultiplier*100}%): {str(int(ATK*charge*finishMultiplier))}")
        else:
            print("No Super Attacks found\n")

def calcDomainStat(characterKit, totalBuff, onAttackStat, crit, superEffective, additional):
    if characterKit.dokkan_fields and domain.get() == 1:
        domainATK = 0
        domainDEF = 0
        dbCursor.execute(f'''SELECT * FROM dokkan_field_efficacies where dokkan_field_efficacy_set_id = {characterKit.dokkan_fields}''')
        domainOutput = dbCursor.fetchall()    
        for domainLine in domainOutput:
            match domainLine[3]:
                case 1: 
                    domainATK += domainLine[8]
                case 2:
                    domainDEF += domainLine[8]
                case 3:
                    domainATK += domainLine[8]
                    domainDEF += domainLine[9]
        domainBuff = [int(totalBuff[0] * (1 + (domainATK/100))), int(totalBuff[1] * (1 + (domainDEF/100)))] # Apply domain buffs
        dbCursor.execute(f'''SELECT * FROM dokkan_fields where dokkan_field_efficacy_set_id = {characterKit.dokkan_fields}''')
        domainOutput = dbCursor.fetchall()   
        if domainATK != 0 or domainDEF != 0:
            print(f'| {domainBuff[0]} | {domainBuff[1]} | (With {domainATK}%/{domainDEF}% Domain Skill Buff: {domainOutput[0][2]})')
        calcStatKi(characterKit, domainBuff, onAttackStat, crit, superEffective, additional)
    else:
        calcStatKi(characterKit, totalBuff, onAttackStat, crit, superEffective, additional)

def calcActiveStat(characterKit, totalBuff, onAttackStat, crit, superEffective, additional):
    atkBuff = 0
    defBuff = 0
    if characterKit.active_skill_set_id and active.get() == 1:
        dbCursor.execute(f'''SELECT * FROM active_skills where active_skill_set_id = {characterKit.active_skill_set_id}''')
        dbOutput = dbCursor.fetchall()
        
        for activeLine in dbOutput:
            match activeLine[5]:
                case 1: atkBuff += activeLine[6]
                case 2: defBuff += activeLine[6]
                case 76: superEffective = True
                case 90: crit = True
    if atkBuff != 0 or defBuff != 0:
        totalBuff[0] = int(totalBuff[0] * (1 + (atkBuff/100)))
        totalBuff[1] = int(totalBuff[1] * (1 + (defBuff/100)))
        print(f'| {totalBuff[0]} | {totalBuff[1]} | (With {54+atkBuff}%/{54+defBuff}% Active Skill Buff)')
    elif gogeta.get() == 1:
        totalBuff[0] = int(totalBuff[0] * (1 + ((54+atkBuff)/100)))
        totalBuff[1] = int(totalBuff[1] * (1 + ((54+defBuff)/100)))
        superEffective = True
        print(f'| {totalBuff[0]} | {totalBuff[1]} | (With {54+atkBuff}%/{54+defBuff}% Active Skill Buff)')
    calcDomainStat(characterKit, totalBuff, onAttackStat, crit, superEffective, additional)

def checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional):
    totalBuff = [characterKit.atk_max, characterKit.def_max]
    # Dev Note: Fix Whitespace spacing
    print('| ATK | DEF |')
    print('-------------')
    print(f'| {totalBuff[0]} | {totalBuff[1]} | (Base Stat)')
    # Duo 200% lead by default
    lead = 5
    # Dev note: Temp condition, manually checks for units supported under 220% leads:
    # - Vegto, Gogta, SSBE, Monke, Rice, Frank, Ultra Vegeta 1, Fishku, Cell Games,
    # U7 Pawn, U6 Pawn, KFC, Serious Tao, Blue Balls, Rosemasu, Gogta 4, Omeger Shawn
    if ((("Earth-Protecting Heroes" in characterKit.categories or 
    "Fused Fighters" in characterKit.categories or
    "Pure Saiyans" in characterKit.categories) and
    ("Earth-Bred Fighters" in characterKit.categories or
    "Potara" in characterKit.categories)) or 
    (("Successors" in characterKit.categories or 
    "Fused Fighters" in characterKit.categories or
    "Pure Saiyans" in characterKit.categories) and
    ("Gifted Warriors" in characterKit.categories or
    "Fusion" in characterKit.categories)) or 
    (("Transformation Boost" in characterKit.categories or 
    "Gifted Warriors" in characterKit.categories) and
    ("Power Beyond Super Saiyan" in characterKit.categories)) or
    (("DB Saga" in characterKit.categories or 
    "Earth-Bred Fighters" in characterKit.categories) and
    ("Youth" in characterKit.categories) or
    ("Dragon Ball Seekers" in characterKit.categories)) or 
    (("Tournament Participants" in characterKit.categories or 
    "Worldwide Chaos" in characterKit.categories) and
    ("Androids" in characterKit.categories) or
    ("Accelerated Battle" in characterKit.categories)) or
    (("Representatives of Universe 7" in characterKit.categories or 
    "Full Power" in characterKit.categories) and
    ("Tournament Participants" in characterKit.categories) or
    ("Super Heroes" in characterKit.categories)) or
    (("Universe 6" in characterKit.categories or 
    "Rapid Growth" in characterKit.categories or 
    "Accelerated Battle" in characterKit.categories) and
    ("Tournament Participants" in characterKit.categories)) or
    (("Mission Execution" in characterKit.categories or 
    "Earth-Bred Fighters" in characterKit.categories) and
    ("Dragon Ball Seekers" in characterKit.categories) or
    ("Earthlings" in characterKit.categories)) or
    (("Future Saga" in characterKit.categories or 
    "Fused Fighters" in characterKit.categories) and
    ("Bond of Parent and Child" in characterKit.categories or
    "Final Trump Card" in characterKit.categories)) or 
    (("Inhuman Deeds" in characterKit.categories or 
    "Power Absorption" in characterKit.categories or 
    "GT Bosses" in characterKit.categories) and
    ("Shadow Dragon Saga" in characterKit.categories or
    "Worldwide Chaos" in characterKit.categories or
    "Battle of Fate" in characterKit.categories)) or 
    (("Hybrid Saiyans" in characterKit.categories or 
    "Youth" in characterKit.categories or 
    "Defenders of Justice" in characterKit.categories) and
    ("Sibling's Bond" in characterKit.categories or
    "Bond of Parent and Child" in characterKit.categories or
    "Bond of Friendship" in characterKit.categories)) or 
    (("Movie Heroes" in characterKit.categories or 
    "Movie Bosses" in characterKit.categories) and
    ("Transformation Boost" in characterKit.categories or
    "Gifted Warriors" in characterKit.categories or
    "Inhuman Deeds" in characterKit.categories)) or
    "Universe Survival Saga" in characterKit.categories or 
    "Giant Ape Power" in characterKit.categories or
    "Full Power" in characterKit.categories or 
    "Battle of Fate" in characterKit.categories or
    "Universe 6" in characterKit.categories or
    "Super Bosses" in characterKit.categories or
    "GT Heroes" in characterKit.categories or
    "Exploding Rage" in characterKit.categories):
        lead = 5.4
    totalBuff[0] = int(totalBuff[0]*lead) # Apply leader skill
    totalBuff[1] = int(totalBuff[1]*lead) # Apply leader skill
    print(f'| {totalBuff[0]} | {totalBuff[1]} | (With Duo {int(((lead-1)*100)/2)}% Leader Skill)')
    
    """Collects the names of all checked items."""
    '''checked_items = []
    for i, var in enumerate(atkdefVars):
        #if var.get() == 1:
            # ATK += onAttackStat[0][i][1]
            # DEF += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[0][i])
    for i, var in enumerate(atkVars):
        #if var.get() == 1:
            # ATK += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[1][i])
    for i, var in enumerate(defVars):
        #if var.get() == 1:
            # DEF += onAttackStat[0][i][1]
        #    checked_items.append(condSoTStat[2][i])'''
    newBuff = [int(totalBuff[0] * (1 + (atkPerBuff/100))), int(totalBuff[1] * (1 + (defPerBuff/100)))] # Apply SoT percentage buffs
    print(f'| {newBuff[0]} | {newBuff[1]} | (With {atkPerBuff}%/{defPerBuff}% Passive Buff)')
    newBuff[0] += int(atkFlatBuff) # Apply SoT flat buffs
    newBuff[1] += int(defFlatBuff) # Apply SoT flat buffs
    print(f'| {newBuff[0]} | {newBuff[1]} | (With {atkFlatBuff}/{defFlatBuff} Flat Passive Buff)')
    newBuff[0] = int(newBuff[0] * (1 + (linkBuffs[0]/100))) # Apply link buffs
    newBuff[1] = int(newBuff[1] * (1 + (linkBuffs[1]/100))) # Apply link buffs
    print(f'| {newBuff[0]} | {newBuff[1]} | (With {linkBuffs[0]}%/{linkBuffs[1]}% Link Skill Buff)')
    
    calcActiveStat(characterKit, newBuff, onAttackStat, crit, superEffective, additional)
    return

def findCond(characterKit, dbOutput, cond):
    if not cond:
        return ''
    dbCursor.execute(f'''SELECT * FROM skill_causalities where id = {cond}''')
    skillOutput = dbCursor.fetchall()
    match skillOutput[0][1]:
        case 1: return f'When HP is {skillOutput[0][2]}% or more'
        case 2: return f'When HP is {skillOutput[0][2]}% or less'
        case 3:
            if characterKit.rarity != 'LR':
                if dbOutput[0][2] != 1: return f'When Ki is {math.ceil((skillOutput[0][2]/400)*characterKit.eball_mod_max_num)} or more'
                else: return f'When Ki is {math.ceil((skillOutput[0][2]/400)*characterKit.eball_mod_max_num)} or more'
            return f'When Ki is {math.ceil((skillOutput[0][2]/800)*characterKit.eball_mod_max_num)} or more'
        case 4:
            if characterKit.rarity != 'LR':
                if dbOutput[0][2] != 1: return f'When Ki is {math.floor((skillOutput[0][2]/400)*characterKit.eball_mod_max_num)} or less'
                else: return f'When Ki is {math.floor((skillOutput[0][2]/400)*characterKit.eball_mod_max_num)} or less'
            return f'When Ki is {math.floor((skillOutput[0][2]/800)*characterKit.eball_mod_max_num)} or less'
        case 5: return f'After {dbOutput[0][2]} turn(s) from start of battle'
        case 6: return f'When all team members have "{skillOutput[0][2]}"'
        case 7: return f'When enemy has "{skillOutput[0][2]}"'
        case 8: return f'When ATK is {skillOutput[0][2]} or more and DEF is {skillOutput[0][3]} or more'
        case 9: return f'When ATK is {skillOutput[0][2]} or less and DEF is {skillOutput[0][3]} or less'
        case 10: return f'When HP is {skillOutput[0][2]}% or above and Ki is above {skillOutput[0][3]}'
        case 11: return f'When HP is {skillOutput[0][2]}% or above and Ki is below {skillOutput[0][3]}'
        case 12: return f'When HP is {skillOutput[0][2]}% or below and Ki is above {skillOutput[0][3]}'
        case 13: return f'When HP is {skillOutput[0][2]}% or below and Ki is below {skillOutput[0][3]}'
        case 14: return 'As the first attacker in a turn'
        case 15: return f'When facing {skillOutput[0][2]} or more enemies'
        case 16: return f'When facing less than {skillOutput[0][2]} enemies'
        case 17: return f"When the enemy's HP is {skillOutput[0][2]}% or above"
        case 18: return f"When the enemy's HP is {skillOutput[0][2]}% or below"
        case 19: return f'Slot {skillOutput[0][2]+1}'
        case 20: return f'When Ki is {skillOutput[0][2]}% or above'
        case 21: return f'When Ki is {skillOutput[0][2]}% or below'
        case 22: return f'With {skillOutput[0][2]} on the team'
        case 23: return f'With {skillOutput[0][2]} or more links activated'
        case 24: return '# attacks received'
        case 25: return 'When enemy is killed'
        case 26: return f'When HP is {skillOutput[0][2]}% or more and card has enough Ki to perform a Super Attack'
        case 27: return f'When HP is {skillOutput[0][2]}% or less and card has enough Ki to perform a Super Attack'
        case 28: return f'When there is a {skillOutput[0][2]} Type ally on rotation'
        case 29: return f'When facing "{skillOutput[0][2]}" as an enemy'
        case 30: return 'When guard is activated'
        case 31: return
        case 32: return
        case 33: return 
        case 33: return f'When HP is between {skillOutput[0][2]}% and {skillOutput[0][3]}%'
        case 34:
            dbCursor.execute(f'''SELECT * FROM card_categories where id = {skillOutput[0][3]}''')
            category = dbCursor.fetchall()[0][1]
            if skillOutput[0][2] == 0:  return f'With {skillOutput[0][4]} "{category}" allies on the team'
            elif skillOutput[0][2] == 1: return f'With {skillOutput[0][4]} "{category}" enemy'
            elif skillOutput[0][2] == 2: return f'With {skillOutput[0][4]} "{category}" allies on rotation' 
        case 37: return f'When HP is below percent, battle has past turn number'
        case 38: return 'With status effect'
        case 39:
            if skillOutput[0][2] == 32: return f'When facing a Super Class enemy'
            return 'When facing an Extreme Class enemy'
        case 40: return '# Super Attacks performed'
        case 41: return 'With character'
        case 42:
            if skillOutput[0][2] == 1: return f'With {skillOutput[0][3]} AGL Ki Spheres obtained'
            elif skillOutput[0][2] == 2: return f'With {skillOutput[0][3]} TEQ Ki Spheres obtained'
            elif skillOutput[0][2] == 4: return f'With {skillOutput[0][3]} INT Ki Spheres obtained'
            elif skillOutput[0][2] == 8: return f'With {skillOutput[0][3]} STR Ki Spheres obtained'
            elif skillOutput[0][2] == 16: return f'With {skillOutput[0][3]} PHY Ki Spheres obtained'
            elif skillOutput[0][2] == 32: return f'With {skillOutput[0][3]} Rainbow Ki Spheres obtained'
            else: return f'With {skillOutput[0][3]} Ki Spheres obtained'
        case 43: return '# attacks evaded'
        case 44:
            if skillOutput[0][2] == 1: return f'{skillOutput[0][2]} Super Attacks performed'
            elif skillOutput[0][2] == 2: return f'{skillOutput[0][2]} attacks performed'
            elif skillOutput[0][2] == 3: return f'{skillOutput[0][2]} attacks received'
            elif skillOutput[0][2] == 4: return f'Guard activated {skillOutput[0][2]} times'
            elif skillOutput[0][2] == 5: return f'{skillOutput[0][2]} attacks evaded'
        case 45: return ''
        case 46:
            if skillOutput[0][3] == 32:
                #if skillOutput[0][2] == 0: return 'When facing an Extreme Class enemy'
                if skillOutput[0][2] == 1: return 'When facing an Super Class enemy'
                #elif skillOutput[0][2] == 2:return 'When facing an Extreme Class enemy'
            elif skillOutput[0][3] == 64:
                #if skillOutput[0][2] == 0: return 'When facing an Extreme Class enemy'
                if skillOutput[0][2] == 1: return 'When facing an Extreme Class enemy'
                #elif skillOutput[0][2] == 2: return 'When facing an Extreme Class enemy'
            #0 for deck; 1 for enemy; 2 for ally attacking in the same turn	
            #if skillOutput[0][2] == 32:
            #    return f'When facing a Super Class enemy'
            #return 'When facing an Extreme Class enemy'
            
            
            return ''
        case 47: return 'After revival'
        case 48: return ''
        case 49: return ''
        case 51: return f'For {skillOutput[0][2]} turn(s) from entry'
        case 52: return ''
        case 53: return ''
        case 54: return ''
        case 55: return f'{skillOutput[0][2]} turn(s) passed'
        case 56: return ''
        case 57:
            characterKit.dokkan_fields = skillOutput[0][2]
            return '57'
        case 58: return ''
        case 59: return ''
        case 60: return ''
        case 61: return 'After receiving an attack'
        case 62: return ''
        case 63: return ''
        case 64: return ''
        case 65: return ''
        case 66: return ''

# Read through kit, sepearate lines based on activiation condition (SoT vs. 'on attack')
# Then, calculate SoT attack and conditional SoT attack  
def calculateMain(characterKit, dbCursor, atkLinkBuffs, defLinkBuffs, crit):   
    passive_skill_set_id = characterKit.passive_skill_set_id
    atkPerBuff = 0
    defPerBuff = 0
    atkFlatBuff = 0
    defFlatBuff = 0
    condSoTATK = []
    condSoTATKDEF = []
    condSoTDEF = []
    onAttackATK = []
    onAttackATKDEF = []
    onAttackDEF = []
    additional = 0
    superEffective = False
    
    if characterKit.rarity == 'UR' or characterKit.rarity == 'LR':
        additional += 1
    
    if characterKit.passive_skill_set_id:
        while True:
            dbCursor.execute(f'''SELECT * FROM passive_skills where id = {passive_skill_set_id}''')
            dbOutput = dbCursor.fetchall()
            if len(dbOutput) == 0:
                break
            
            # Skips enemy debuffs and (self excluded)
            if (dbOutput[0][4] == 3 or dbOutput[0][4] == 4 or
            dbOutput[0][4] == 14 or dbOutput[0][4] == 15 or
            dbOutput[0][4] == 16):
                passive_skill_set_id += 1000000
                continue
            # Recovery, Ki raise, damage reduction, guard, type Ki, dodge, nullification
            elif (dbOutput[0][3] == 4 or dbOutput[0][3] == 5 or
            dbOutput[0][3] == 13 or dbOutput[0][3] == 20 or
            dbOutput[0][3] == 51 or dbOutput[0][3] == 67 or
            dbOutput[0][3] == 78 or dbOutput[0][3] == 83 or
            dbOutput[0][3] == 91 or dbOutput[0][3] == 92 or
            dbOutput[0][3] == 110 or dbOutput[0][3] == 119):
                passive_skill_set_id += 1000000
                continue
            # Domain Skill via passive (LR Future Gohan, STR Slug, STR Cell)
            elif dbOutput[0][3] == 0:
                dbCursor.execute(f'''SELECT * FROM dokkan_field_passive_skill_relations where passive_skill_id = {dbOutput[0][0]}''')
                domainOutput = dbCursor.fetchall()    
                characterKit.dokkan_fields = domainOutput[0][1]
                passive_skill_set_id += 1000000
                continue
            
            if dbOutput[0][4] == 2 and dbOutput[0][5] != 0:
                dbCursor.execute(f'''SELECT * FROM sub_target_types where sub_target_type_set_id = {dbOutput[0][5]}''')
                supportOutput = dbCursor.fetchall()
                dbCursor.execute(f'''SELECT * FROM card_categories where id = {supportOutput[0][3]}''')
                supportOutput2 = dbCursor.fetchall()
                # Skips support passives that don't apply to character (LR Babidi & Dabura)
                if supportOutput2[0][1] not in characterKit.categories:
                    passive_skill_set_id += 1000000
                    continue
                
            cond = ''
            stat = 0
            if dbOutput[0][11]:
                id = ''
                for character in dbOutput[0][11][dbOutput[0][11].find(': "')+3:dbOutput[0][11].find('",')]:
                    if character == ')':
                        line = findCond(characterKit, dbOutput, id)
                        cond += line + ')'
                        id = ''
                    elif character == '(':
                        line = findCond(characterKit, dbOutput, id)
                        cond += '(' + line
                        id = ''
                    elif character == '|':
                        line = findCond(characterKit, dbOutput, id)
                        cond += line + ' OR '
                        id = ''
                    elif character == '&':
                        line = findCond(characterKit, dbOutput, id)
                        cond += line + ' AND '
                        id = ''
                    else:
                        id += character
                line = findCond(characterKit, dbOutput, id)
                cond += line
            if cond.__contains__('57'):
                passive_skill_set_id += 1000000
                continue
                
            prob = 100
            # If line doesn't have a 100% chance to activate
            if dbOutput[0][10] != 100:
                prob = dbOutput[0][10]
            turn = dbOutput[0][8]
            
            cond2 = ''
            match dbOutput[0][3]:
                case 1 | 16 | 59: stat = 1 # ATK
                case 2 | 60: stat = 2 # DEF
                case 3 | 61: stat = 0 # ATK & DEF
                case 68:
                    if dbOutput[0][13] == 1: stat = 1
                    elif dbOutput[0][13] == 3: stat = 2
                    else:
                        passive_skill_set_id += 1000000
                        continue
                case 71: 
                    if not cond2:
                        cond2 = 'The more HP remaining'
                    else:
                        cond2 = 'The more HP remaining, '
                    stat = 1
                case 76:
                    superEffective = True
                    passive_skill_set_id += 1000000
                    continue
                case 79 | 103:
                    characterKit.transformation = dbOutput[0][12]
                    passive_skill_set_id += 1000000
                    continue
                case 81:
                    additional += 1
                    passive_skill_set_id += 1000000
                    continue
                case 90:
                    crit = True
                    passive_skill_set_id += 1000000
                    continue
                case 98:
                    if not cond2:
                        cond2 = '# actions performed'
                    else:
                        cond2 = ', # actions performed'
                    match dbOutput[0][14]:
                        case 0:
                            stat = 1
                        case 1:
                            stat = 2
                        case _:
                            crit = True
                            passive_skill_set_id += 1000000
                            continue
                #case 120 | 128:
                    #onAttackATK.append(['Counter', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7], dbOutput[0][2], dbOutput[0][10]])
                    #passive_skill_set_id += 1000000
                    #continue
            
            if not dbOutput[0][2] == 1:
                if not cond2:
                    cond2 = 'When attacking'
                else:
                    cond2 += ', when attacking'
                    
            if dbOutput[0][3] == 61:
                if not cond2:
                    cond2 = '# Ki Spheres obtained'
                else:
                    cond2 += ', # Ki Spheres obtained'
            elif dbOutput[0][3] == 68:
                match dbOutput[0][12]:
                    case 1:
                        if not cond2:
                            cond2 = '# AGL Ki Spheres obtained'
                        else:
                            cond2 += ', # AGL Ki Spheres obtained'
                    case 2:
                        if not cond2:
                            cond2 = '# TEQ Ki Spheres obtained'
                        else:
                            cond2 += ', # TEQ Ki Spheres obtained'
                    case 4:
                        if not cond2:
                            cond2 = '# INT Ki Spheres obtained'
                        else:
                            cond2 += ', # INT Ki Spheres obtained'
                    case 8:
                        if not cond2:
                            cond2 = '# STR Ki Spheres obtained'
                        else:
                            cond2 += ', # STR Ki Spheres obtained'
                    case 16:
                        if not cond2:
                            cond2 = '# PHY Ki Spheres obtained'
                        else:
                            cond2 += ', # PHY Ki Spheres obtained'
            
            if dbOutput[0][9] == 1:
                if not cond2:
                    cond2 = 'Once only'
                else:
                    cond2 += ', once only'
            
            # If class buff and character not in class
            if ((dbOutput[0][4] == 12 and characterKit.awakening_element_type != 'Super') or
            (dbOutput[0][4] == 13 and characterKit.awakening_element_type != 'Extreme')):
                passive_skill_set_id += 1000000
                continue 
            # If type buff and character is not in type
            elif ((dbOutput[0][3] == 16 or dbOutput[0][3] == 17 or dbOutput[0][3] == 18) and
            ((dbOutput[0][12] == 0 and characterKit.element != 'AGL') or
            (dbOutput[0][12] == 1 and characterKit.element != 'TEQ') or
            (dbOutput[0][12] == 2 and characterKit.element != 'INT') or
            (dbOutput[0][12] == 3 and characterKit.element != 'STR') or
            (dbOutput[0][12] == 4 and characterKit.element != 'PHY'))):
                passive_skill_set_id += 1000000
                continue
            
            if not cond and prob == 100 and dbOutput[0][2] == 1 and not cond2:
                match stat:
                    case 0:
                        if dbOutput[0][3] == 18:
                            if dbOutput[0][7] == 0: # Flat ATK & DEF raise
                                atkFlatBuff += dbOutput[0][13]
                                defFlatBuff += dbOutput[0][14]
                            elif dbOutput[0][7] == 1: # Flat ATK & DEF lower
                                atkFlatBuff -= dbOutput[0][13]
                                defFlatBuff += dbOutput[0][14]
                            elif dbOutput[0][7] == 2: # Percent ATK & DEF raise
                                atkPerBuff += dbOutput[0][13]
                                defPerBuff += dbOutput[0][14]
                            elif dbOutput[0][7] == 3: # Percent ATK & DEF lower
                                atkPerBuff -= dbOutput[0][13]
                                defPerBuff += dbOutput[0][14]
                        elif dbOutput[0][3] == 82:
                            if dbOutput[0][7] == 0: # Flat ATK & DEF raise
                                atkFlatBuff += dbOutput[0][13]
                                defFlatBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 1: # Flat ATK & DEF lower
                                atkFlatBuff -= dbOutput[0][13]
                                defFlatBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 2: # Percent ATK & DEF raise
                                atkPerBuff += dbOutput[0][13]
                                defPerBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 3: # Percent ATK & DEF lower
                                atkPerBuff -= dbOutput[0][13]
                                defPerBuff += dbOutput[0][13]
                        else:
                            if dbOutput[0][7] == 0: # Flat ATK & DEF raise
                                atkFlatBuff += dbOutput[0][12]
                                defFlatBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 1: # Flat ATK & DEF lower
                                atkFlatBuff -= dbOutput[0][12]
                                defFlatBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 2: # Percent ATK & DEF raise
                                atkPerBuff += dbOutput[0][12]
                                defPerBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 3: # Percent ATK & DEF lower
                                atkPerBuff -= dbOutput[0][12]
                                defPerBuff += dbOutput[0][13]
                    case 1:
                        if dbOutput[0][3] == 16:
                            if dbOutput[0][7] == 0: # Flat ATK raise
                                atkFlatBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 1: # Flat ATK lower
                                atkFlatBuff -= dbOutput[0][13]
                            elif dbOutput[0][7] == 2: # Percent ATK raise
                                atkPerBuff += dbOutput[0][13]
                            elif dbOutput[0][7] == 3: # Percent ATK lower
                                atkPerBuff -= dbOutput[0][13]
                        # Normal SoT Buffs
                        else:
                            if dbOutput[0][7] == 0: # Flat ATK raise
                                atkFlatBuff += dbOutput[0][12]
                            elif dbOutput[0][7] == 1: # Flat ATK lower
                                atkFlatBuff -= dbOutput[0][12]
                            elif dbOutput[0][7] == 2: # Percent ATK raise
                                atkPerBuff += dbOutput[0][12]
                            elif dbOutput[0][7] == 3: # Percent ATK lower
                                atkPerBuff -= dbOutput[0][12]
                    case 2:
                        if dbOutput[0][7] == 0: # Flat DEF raise
                            defFlatBuff += dbOutput[0][12]
                        elif dbOutput[0][7] == 1: # Flat DEF lower
                            defFlatBuff -= dbOutput[0][12]
                        elif dbOutput[0][7] == 2: # Percent DEF raise
                            defPerBuff += dbOutput[0][12]
                        elif dbOutput[0][7] == 3: # Percent DEF lower
                            defPerBuff -= dbOutput[0][12]
            else:
                match dbOutput[0][2]:
                    case 1:
                        if dbOutput[0][3] == 18:
                            match stat:
                                case 0: condSoTATKDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                                case 1: condSoTATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                                case 2: condSoTDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                        elif dbOutput[0][3] == 68:
                            match stat:
                                case 1: condSoTATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][14], 0, dbOutput[0][7]])
                                case 2: condSoTDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][14], 0, dbOutput[0][7]])
                        else:
                            match stat:
                                case 0: condSoTATKDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
                                case 1: condSoTATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
                                case 2: condSoTDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
                    case _:
                        if dbOutput[0][3] == 18:
                            match stat:
                                case 0: onAttackATKDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                                case 1: onAttackATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                                case 2: onAttackDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][13], dbOutput[0][14], dbOutput[0][7]])
                        elif dbOutput[0][3] == 68:
                            match stat:
                                case 1: onAttackATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][14], 0, dbOutput[0][7]])
                                case 2: onAttackDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][14], 0, dbOutput[0][7]])
                        else:
                            match stat:
                                case 0: onAttackATKDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
                                case 1: onAttackATK.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
                                case 2: onAttackDEF.append([f'{cond} ({cond2}) ({prob}% chance) (For {turn} turn(s))', dbOutput[0][12], dbOutput[0][13], dbOutput[0][7]])
            passive_skill_set_id += 1000000
    
    condSoTStat = [condSoTATKDEF, condSoTATK, condSoTDEF]
    onAttackStat = [onAttackATKDEF, onAttackATK, onAttackDEF]
    totalBuff = [characterKit.atk_max, characterKit.def_max]
    linkBuffs = [atkLinkBuffs, defLinkBuffs]
    
    # Create six individual panels within the bottom frame
    ATKDEFFrame = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightblue")
    ATKDEFFrame.grid(row=8, column=0, padx=5, pady=5)
    ATKFrame = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightgreen")
    ATKFrame.grid(row=8, column=1, padx=5, pady=5)
    DEFFrame = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightcoral")
    DEFFrame.grid(row=8, column=2, padx=5, pady=5)
    ATKDEFFrame2 = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightblue")
    ATKDEFFrame2.grid(row=9, column=0, padx=5, pady=5)
    ATKFrame2 = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightgreen")
    ATKFrame2.grid(row=9, column=1, padx=5, pady=5)
    DEFFrame2 = tk.Frame(root, highlightbackground="black", highlightthickness=1, bg="lightcoral")
    DEFFrame2.grid(row=9, column=2, padx=5, pady=5)
    
    # Clears all stat frames
    for widget in ATKDEFFrame.winfo_children():
        widget.destroy()
    ATKDEFFrame.pack_forget()
    for widget in ATKFrame.winfo_children():
        widget.destroy()
    ATKFrame.pack_forget()
    for widget in DEFFrame.winfo_children():
        widget.destroy()
    DEFFrame.pack_forget()
    for widget in ATKDEFFrame2.winfo_children():
        widget.destroy()
    ATKDEFFrame2.pack_forget()
    for widget in ATKFrame2.winfo_children():
        widget.destroy()
    ATKFrame2.pack_forget()
    for widget in DEFFrame2.winfo_children():
        widget.destroy()
    DEFFrame2.pack_forget()
    
    for line in condSoTATKDEF:
        checkbox = tk.Checkbutton(ATKDEFFrame, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    for line in condSoTATK:
        checkbox = tk.Checkbutton(ATKFrame, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    for line in condSoTDEF:
        checkbox = tk.Checkbutton(DEFFrame, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    for line in onAttackATKDEF:
        checkbox = tk.Checkbutton(ATKDEFFrame2, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    for line in onAttackATK:
        checkbox = tk.Checkbutton(ATKFrame2, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    for line in onAttackDEF:
        checkbox = tk.Checkbutton(DEFFrame2, text=line[0], variable=line, command=lambda: checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional))
        checkbox.pack(anchor=W)
    
    print(characterKit.name)
    print(f"Initial percent buffs: {atkPerBuff}% ATK, {defPerBuff}% DEF")
    print(f"Initial flat buffs: {atkFlatBuff} ATK, {defFlatBuff} DEF\n")
    checkCond(characterKit, totalBuff, condSoTStat, atkPerBuff, defPerBuff, atkFlatBuff, defFlatBuff, linkBuffs, onAttackStat, crit, superEffective, additional)
    
# Read through kit, sepearate lines based on activiation condition (SoT vs. 'on attack')
# Then, calculate SoT defense and conditional SoT defense  
def calculateLinks(characterKit, partnerKit, dbCursor):
    os.system('cls')
        
    # Find all shared links
    shared = False
    kiLinkBuffs = 0
    atkLinkBuffs = 0
    defLinkBuffs = 0
    critLinkBuffs = 0
    evadeLinkBuffs = 0
    damageReduceLinkBuffs = 0
    recoveryLinkBuffs = 0
    defLinkDebuffs = 0
    crit = False
    if (characterKit.name != partnerKit.name or
    (int(partnerKit.id) >= 4000000 and characterKit.id != partnerKit.id)):
        for sharedLink in characterKit.card_links:
            if sharedLink in partnerKit.card_links:
                shared = True
                dbCursor.execute(f'''SELECT * FROM link_skills where id = {sharedLink}''')
                dbOutput = dbCursor.fetchall()[0]
                linkName = dbOutput[1]
                dbCursor.execute(f'''SELECT * FROM link_skill_lvs where id = {sharedLink}10''')
                dbOutput = dbCursor.fetchall()[0]
                linkBuff = dbOutput[3]
                # linkLabel = tk.Label(root, text=f'{linkName} - {linkBuff}')
                # linkLabel.grid(row=0, column=1, padx=5, pady=5)
                
                dbCursor.execute(f'''SELECT * FROM link_skill_efficacies where link_skill_lv_id = {sharedLink}10''')
                dbOutput = dbCursor.fetchall()
                for linkBuff in dbOutput:
                    match linkBuff[3]:
                        case 1:
                            atkLinkBuffs += int(linkBuff[11])
                        case 2:
                            if linkBuff[4] == 4:
                                defLinkDebuffs += int(linkBuff[11])
                            else:
                                defLinkBuffs += int(linkBuff[11])
                        case 3:
                            atkLinkBuffs += int(linkBuff[11])
                            defLinkBuffs += int(linkBuff[12])
                        case 4:
                            recoveryLinkBuffs += int(linkBuff[11])
                        case 5:
                            kiLinkBuffs += int(linkBuff[11])
                        case 13:
                            damageReduceLinkBuffs += (100 - int(linkBuff[11]))
                        case 90:
                            crit = True
                            critLinkBuffs += int(linkBuff[11])
                        case 91:
                            evadeLinkBuffs += int(linkBuff[11])
    else:
        # linkLabel = tk.Label(root, text='Unit cannot link with partner (Shared name)')
        #if not partneridEntry.get():
            # linkLabel = tk.Label(root, text='No partner linked')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        calculateMain(characterKit, dbCursor, 0, 0, False)
        return

    if not shared:
        # linkLabel = tk.Label(root, text='Unit cannot link with partner (No shared links)')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        calculateMain(characterKit, dbCursor, 0, 0, False)
        return
    else:
        # linkLabel = tk.Label(root, text='\nTotal Link Buffs:')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f'- Ki +{str(kiLinkBuffs)}, ATK +{str(atkLinkBuffs)}%, DEF +{str(defLinkBuffs)}%')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f'- Chance of performing a critical hit +{str(critLinkBuffs)}%')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f"- Chance of evading enemy's attack +{evadeLinkBuffs}%")
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f'- Damage reduction rate +{damageReduceLinkBuffs}%')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f'- Recovers {recoveryLinkBuffs}% HP')
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        # linkLabel = tk.Label(root, text=f"- All enemies' DEF -{defLinkDebuffs}%")
        # linkLabel.grid(row=0, column=1, padx=5, pady=5)
        
        calculateMain(characterKit, dbCursor, atkLinkBuffs, defLinkBuffs, crit)
   
# Helper method to get all unit details
def getPartnerKit(partnerID):
    if partnerID % 2 == 0:
        partnerID += 1
    partnerKit = Partner(partnerID, '', '', 0, [])
    
    dbCursor.execute(f'''SELECT * FROM cards where id = {partnerID}''')
    print("Partner sucessfully loaded.")
    dbOutput = dbCursor.fetchall()
    
    partnerKit.name = dbOutput[0][1]
    match dbOutput[0][5]:
        case 0:
            partnerKit.rarity = 'N'
        case 1:
            partnerKit.rarity = 'R'
        case 2:
            partnerKit.rarity = 'SR'
        case 3:
            partnerKit.rarity = 'SSR'
        case 4:
            partnerKit.rarity = 'UR'
        case 5:
            partnerKit.rarity = 'LR'
    match dbOutput[0][12]:
        case 0 | 10 | 20:
            partnerKit.element = 'AGL'
            partnerLabel['highlightbackground'] = '#12104E'
        case 1 | 11 | 21:
            partnerKit.element = 'TEQ'
            partnerLabel['highlightbackground'] = '#1F4D0A'
        case 2 | 12 | 22:
            partnerKit.element = 'INT'
            partnerLabel['highlightbackground'] = '#48104E'
        case 3 | 13 | 23:
            partnerKit.element = 'STR'
            partnerLabel['highlightbackground'] = '#480F0E'
        case 4 | 14 | 24:
            partnerKit.element = 'PHY'
            partnerLabel['highlightbackground'] = '#7B5B05'
    for i in range(0, 7):
        partnerKit.card_links.append(dbOutput[0][23+i])
                        
    if partnerID >= 4000000:
        partnerKit.name += (' (<->)')
            
    os.system('cls')
    return partnerKit   

# Helper method to get all unit details
def getKit(characterID, dbCursor, EZA):    
    if characterID % 2 == 0:
        characterID += 1
    characterKit = Unit(characterID, '', '', 0, 0, 0, '', '', 0, 0, 0, 0, 0, '', 0, 0, [],
    [], [], [], 0, [], [], [], [])
    
    dbCursor.execute(f'''SELECT * FROM cards where id = {characterID}''')
    print("Card sucessfully loaded.")
    dbOutput = dbCursor.fetchall()
    
    characterKit.name = dbOutput[0][1]
    match dbOutput[0][5]:
        case 0:
            characterKit.rarity = 'N'
        case 1:
            characterKit.rarity = 'R'
        case 2:
            characterKit.rarity = 'SR'
        case 3:
            characterKit.rarity = 'SSR'
        case 4:
            characterKit.rarity = 'UR'
        case 5:
            characterKit.rarity = 'LR'
    characterKit.hp_max = dbOutput[0][7]
    characterKit.atk_max = dbOutput[0][9]
    characterKit.def_max = dbOutput[0][11]
    match dbOutput[0][12]:
        case 0 | 10 | 20:
            characterKit.element = 'AGL'
            mainLabel['highlightbackground'] = '#12104E'
        case 1 | 11 | 21:
            characterKit.element = 'TEQ'
            mainLabel['highlightbackground'] = '#1F4D0A'
        case 2 | 12 | 22:
            characterKit.element = 'INT'
            mainLabel['highlightbackground'] = '#48104E'
        case 3 | 13 | 23:
            characterKit.element = 'STR'
            mainLabel['highlightbackground'] = '#480F0E'
        case 4 | 14 | 24:
            characterKit.element = 'PHY'
            mainLabel['highlightbackground'] = '#7B5B05'
    characterKit.skill_lv_max = dbOutput[0][14]
    characterKit.optimal_awakening_growths = dbOutput[0][16]
    characterKit.passive_skill_set_id = dbOutput[0][21]
    characterKit.leader_skill = dbOutput[0][22]
    for i in range(0, 7):
        characterKit.card_links.append(dbOutput[0][23+i])
    characterKit.eball_mod_mid = dbOutput[0][32]
    characterKit.eball_mod_mid_num = dbOutput[0][33]
    characterKit.eball_mod_max = dbOutput[0][34]
    characterKit.eball_mod_max_num = dbOutput[0][35]
    match dbOutput[0][51]:
        case 1:
            characterKit.awakening_element_type = 'Super'
        case 2:
            characterKit.awakening_element_type = 'Extreme'
    
    # Dev Note: Fix EZA/SEZA default case when EZA/SEZA is selected, but unit does not have EZA/SEZA
    if dbOutput[0][16] and EZA != 0:
        ezaCursor = dbConnect.cursor()
        ezaCursor.execute(f'''SELECT max(step) FROM optimal_awakening_growths where optimal_awakening_grow_type = {dbOutput[0][16]}''')
        ezaOutput = ezaCursor.fetchall()[0][0]
        if EZA == 1:
            if characterKit.rarity == 'UR':
                characterKit.hp_max = int(((dbOutput[0][7]-dbOutput[0][6])*.4839)+dbOutput[0][7])
                characterKit.atk_max = int(((dbOutput[0][9]-dbOutput[0][8])*.4839)+dbOutput[0][9])
                characterKit.def_max = int(((dbOutput[0][11]-dbOutput[0][10])*.4839)+dbOutput[0][11])
                ezaCursor.execute(f'''SELECT * FROM optimal_awakening_growths where optimal_awakening_grow_type = {dbOutput[0][16]} AND step = 7''')
            elif characterKit.rarity == 'LR':
                ezaCursor.execute(f'''SELECT * FROM optimal_awakening_growths where optimal_awakening_grow_type = {dbOutput[0][16]} AND step = 3''')
            ezaOutput = ezaCursor.fetchall()
            characterKit.skill_lv_max = ezaOutput[0][4]
            characterKit.passive_skill_set_id = ezaOutput[0][5]
            characterKit.leader_skill = ezaOutput[0][6]
        elif EZA == 2:
            if characterKit.rarity == 'UR':
                characterKit.hp_max = int(((dbOutput[0][7]-dbOutput[0][6])*.4839)+dbOutput[0][7])
                characterKit.atk_max = int(((dbOutput[0][9]-dbOutput[0][8])*.4839)+dbOutput[0][9])
                characterKit.def_max = int(((dbOutput[0][11]-dbOutput[0][10])*.4839)+dbOutput[0][11])
                ezaCursor.execute(f'''SELECT * FROM optimal_awakening_growths where optimal_awakening_grow_type = {dbOutput[0][16]} AND step = 8''')
            elif characterKit.rarity == 'LR':
                ezaCursor.execute(f'''SELECT * FROM optimal_awakening_growths where optimal_awakening_grow_type = {dbOutput[0][16]} AND step = 4''')
            ezaOutput = ezaCursor.fetchall()
            characterKit.skill_lv_max = ezaOutput[0][4]
            characterKit.passive_skill_set_id = ezaOutput[0][5]
            characterKit.leader_skill = ezaOutput[0][6]
        else:
            characterKit.passive_skill_itemized_desc = dbOutput[0][21]
            characterKit.leader_skill = dbOutput[0][22]
    
    dbCursor.execute(f'''SELECT * FROM card_specials where card_id = {characterID}''')
    dbOutput = dbCursor.fetchall()
    for special in dbOutput:
        if EZA != 0:
            ezaCursor = dbConnect.cursor()
            ezaCursor.execute(f'''SELECT * FROM special_sets where id = {special[2]}''')
            ezaOutput = ezaCursor.fetchall()
            if EZA != 0 and ezaOutput[0][1].__contains__("Extreme"):
                characterKit.specials.append(tuple([special[2], special[6], special[9], special[12]]))
            elif EZA == 0 and not ezaOutput[0][1].__contains__("Extreme"):
                characterKit.specials.append(tuple([special[2], special[6], special[9], special[12]]))
        else:
            characterKit.specials.append(tuple([special[2], special[6], special[9], special[12]]))
    
    dbCursor.execute(f'''SELECT * FROM card_active_skills where card_id = {characterID}''')
    dbOutput = dbCursor.fetchall()
    if dbOutput:
        characterKit.active_skill_set_id = dbOutput[0][2]
    
        dbCursor.execute(f'''SELECT * FROM dokkan_field_active_skill_set_relations where active_skill_set_id = {dbOutput[0][2]}''')
        dbOutput = dbCursor.fetchall()
        if dbOutput:
            characterKit.dokkan_fields = dbOutput[0][1]
    
    dbCursor.execute(f'''SELECT * FROM cards where id = {characterID}''')
    potentialOutput = dbCursor.fetchall()[0][52] # HiPo
    # Optional selection for GBL/JP kits
    if (characterID == 1004201 or
        characterID == 1003991 or characterID == 1002481 or
        characterID == 1010701 or characterID == 1010661 or
        characterID == 1010631 or characterID == 1011041 or
        characterID == 1010641 or characterID == 1010651 or
        characterID == 1008391 or characterID == 1008381 or
        characterID == 1008371 or characterID == 1008361):
        if input("Test JP Kit? (y/n): ") == 'y':
            match characterID:
                case 1004201: # TEQ SSR/SR Beginner SSJ Goku
                    characterKit.rarity = 'SSR'
                    characterKit.hp_max = 6463
                    characterKit.atk_max = 5869
                    characterKit.def_max = 3299
                    potentialOutput = None
                case 1010641: # INT/STR SR SSJ Angel Goku
                    characterKit.element2 = 'STR'
                case 1010651: # INT/STR SSR SSJ Angel Goku
                    characterKit.element2 = 'STR'
                    potentialOutput = 13
                case 1010631: # STR/INT SSR Pikkon
                    characterKit.element2 = 'INT'
                    characterKit.leader_skill = 101005 # Shhh don't tell anyone I stole this from INT LR Gohan's SSR
                    characterKit.card_links[0] = 16
                    potentialOutput = 22
                case 1011041: # STR/INT UR Pikkon
                    characterKit.element2 = 'INT'
                    characterKit.card_links[4] = 16
                    characterKit.card_links[6] = 118
                    potentialOutput = 22
                    if ezaEntry.get() == 1:
                        characterKit.leader_skill = 1015811 # Here too, Magetta would be really upset if anyone told him, they're already dealing with a lot with having a lower-case 2025 banner unit
                case 1010661: # PHY UR SSJKK Goku
                    characterKit.card_links[6] = 118
                case 1003991: # STR 'Bye Guys' SSJ Goku
                    characterKit.rarity = 'SSR'
                    characterKit.specials[0][2] = 0
                    characterKit.hp_max = 5875
                    characterKit.atk_max = 5050
                    characterKit.def_max = 3188
                    potentialOutput = None
                case 1010701: # TEQ Angel King Cold
                    characterKit.specials[0][0] = 1063 # INT SSJ2 Kale's SA
                case 1002481: # INT Final Form Cooler
                    characterKit.card_links[2] = 39
                case 1008361 | 1008371 | 1008381 | 1008391: # TEQ Kid Goku, INT Nimbus Goku, AGL GT Goku, PHY SSB Goku
                    characterKit.specials[0][2] = 0
    # Clean up for F2P UR TEQ Kid Goku and UR STR Arale (Not properly translated on GBL)
    '''elif characterID == 1010611 or characterID == 1010621:
        match characterID:
                case 1010611:
                    characterKit.title = "Kiiin! Charge"
                    characterKit.name = "Goku (Youth)"
                    characterKit.leader_skill = "STR Type HP +77%"
                    characterKit.passive_skill_name = "Energetic Assault"
                case 1010621:
                    characterKit.title = "Quick Trip on the Magic Cloud"
                    characterKit.name = "Arale Norimaki"
                    characterKit.leader_skill = "TEQ Type HP +77%"
                    characterKit.passive_skill_name = "Child's Ride: Flying Nimbus"'''
        
    if potentialOutput and hipoEntry.get() == 5:
        potential = dbCursor.execute('''SELECT
            potential_boards.id AS 'potential_board_id',
            potential_boards.comment,
            potential_events.type,
            SUM(potential_events.additional_value) AS 'total'
        FROM
            potential_boards
        LEFT JOIN
            potential_squares ON (potential_squares.potential_board_id = potential_boards.id)
        LEFT JOIN
            potential_events ON (potential_events.id = potential_squares.event_id)
        GROUP BY
            potential_events.type,
            potential_squares.potential_board_id
        HAVING
            potential_events.type NOT IN ("PotentialEvent::Select", "PotentialEvent::Skill")
        ORDER BY
            potential_boards.id ASC,
            potential_events.type ASC''')
        potential = potential.fetchall()
        for rank in potential:
            if rank[0] == potentialOutput:
                match rank[2]:
                    case 'PotentialEvent::Hp': characterKit.hp_max += rank[3]
                    case 'PotentialEvent::Atk': characterKit.atk_max += rank[3]
                    case 'PotentialEvent::Defense': characterKit.def_max += rank[3]
    elif potentialOutput and hipoEntry.get() != 0:
        match hipoEntry.get():
            case 1:
                match potentialOutput:
                    case 10 | 11 | 12 | 13 | 14: # F2P
                        characterKit.hp_max += 1200
                        characterKit.atk_max += 1200
                        characterKit.def_max += 1200
                    case 20 | 21 | 22 | 23 | 24: # Summonable
                        characterKit.hp_max += 2000
                        characterKit.atk_max += 2000
                        characterKit.def_max += 2000
                    case 30 | 31 | 32 | 33 | 34: # Summonable (Old)
                        characterKit.hp_max += 2800
                        characterKit.atk_max += 2800
                        characterKit.def_max += 2800
                    case _: # Special HiPo
                        characterKit.hp_max += 1600
                        characterKit.atk_max += 1600
                        characterKit.def_max += 1600
            case 2:
                match potentialOutput:
                    case 10: # AGL F2P
                        characterKit.hp_max += 1980
                        characterKit.atk_max += 2220
                        characterKit.def_max += 2460
                    case 11: # TEQ F2P
                        characterKit.hp_max += 1980
                        characterKit.atk_max += 2460
                        characterKit.def_max += 2220
                    case 12: # INT F2P
                        characterKit.hp_max += 2200
                        characterKit.atk_max += 2200
                        characterKit.def_max += 2200
                    case 13: # STR F2P
                        characterKit.hp_max += 2220
                        characterKit.atk_max += 2460
                        characterKit.def_max += 1980
                    case 14: # PHY F2P
                        characterKit.hp_max += 2460
                        characterKit.atk_max += 2200
                        characterKit.def_max += 1980
                    case 20: # AGL Summonable
                        characterKit.hp_max += 3300
                        characterKit.atk_max += 3700
                        characterKit.def_max += 4100
                    case 21: # TEQ Summonable
                        characterKit.hp_max += 3300
                        characterKit.atk_max += 4100
                        characterKit.def_max += 3700
                    case 22: # INT Summonable
                        characterKit.hp_max += 3700
                        characterKit.atk_max += 3700
                        characterKit.def_max += 3700
                    case 23: # STR Summonable
                        characterKit.hp_max += 3700
                        characterKit.atk_max += 4100
                        characterKit.def_max += 3300
                    case 24: # PHY Summonable
                        characterKit.hp_max += 4100
                        characterKit.atk_max += 3700
                        characterKit.def_max += 3300
                    case 30: # AGL Summonable (Old)
                        characterKit.hp_max += 4620
                        characterKit.atk_max += 5180
                        characterKit.def_max += 5740
                    case 31: # TEQ Summonable (Old)
                        characterKit.hp_max += 4620
                        characterKit.atk_max += 5740
                        characterKit.def_max += 5180
                    case 32: # INT Summonable (Old)
                        characterKit.hp_max += 5180
                        characterKit.atk_max += 5180
                        characterKit.def_max += 5180
                    case 33: # STR Summonable (Old)
                        characterKit.hp_max += 5180
                        characterKit.atk_max += 5740
                        characterKit.def_max += 4620
                    case 34: # PHY Summonable (Old)
                        characterKit.hp_max += 5740
                        characterKit.atk_max += 5180
                        characterKit.def_max += 4620
                    case _: # Special HiPo
                        characterKit.hp_max += 2960
                        characterKit.atk_max += 2960
                        characterKit.def_max += 2960
            case 3:
                match potentialOutput:
                    case 10: # AGL F2P
                        characterKit.hp_max += 2160
                        characterKit.atk_max += 2400
                        characterKit.def_max += 2640
                    case 11: # TEQ F2P
                        characterKit.hp_max += 2160
                        characterKit.atk_max += 2640
                        characterKit.def_max += 2400
                    case 12: # INT F2P
                        characterKit.hp_max += 2400
                        characterKit.atk_max += 2400
                        characterKit.def_max += 2400
                    case 13: # STR F2P
                        characterKit.hp_max += 2400
                        characterKit.atk_max += 2640
                        characterKit.def_max += 2160
                    case 14: # PHY F2P
                        characterKit.hp_max += 2640
                        characterKit.atk_max += 2400
                        characterKit.def_max += 2160
                    case 20: # AGL Summonable
                        characterKit.hp_max += 4000
                        characterKit.atk_max += 4000
                        characterKit.def_max += 4000
                    case 21: # TEQ Summonable
                        characterKit.hp_max += 3600
                        characterKit.atk_max += 4400
                        characterKit.def_max += 4000
                    case 22: # INT Summonable
                        characterKit.hp_max += 4000
                        characterKit.atk_max += 4000
                        characterKit.def_max += 4000
                    case 23: # STR Summonable
                        characterKit.hp_max += 4000
                        characterKit.atk_max += 4400
                        characterKit.def_max += 3600
                    case 24: # PHY Summonable
                        characterKit.hp_max += 4400
                        characterKit.atk_max += 4000
                        characterKit.def_max += 3600
                    case 30: # AGL Summonable (Old)
                        characterKit.hp_max += 5040
                        characterKit.atk_max += 5600
                        characterKit.def_max += 6160
                    case 31: # TEQ Summonable (Old)
                        characterKit.hp_max += 5040
                        characterKit.atk_max += 6160
                        characterKit.def_max += 5600
                    case 32: # INT Summonable (Old)
                        characterKit.hp_max += 5600
                        characterKit.atk_max += 5600
                        characterKit.def_max += 5600
                    case 33: # STR Summonable (Old)
                        characterKit.hp_max += 5600
                        characterKit.atk_max += 6160
                        characterKit.def_max += 5040
                    case 34: # PHY Summonable (Old)
                        characterKit.hp_max += 6160
                        characterKit.atk_max += 5600
                        characterKit.def_max += 5040
                    case _: # Special HiPo
                        characterKit.hp_max += 3200
                        characterKit.atk_max += 3200
                        characterKit.def_max += 3200
            case 4:
                match potentialOutput:
                    case 10: # AGL F2P
                        characterKit.hp_max += 2346
                        characterKit.atk_max += 2820
                        characterKit.def_max += 2826
                    case 11: # TEQ F2P
                        characterKit.hp_max += 2346
                        characterKit.atk_max += 3060
                        characterKit.def_max += 2586
                    case 12: # INT F2P
                        characterKit.hp_max += 2586
                        characterKit.atk_max += 2820
                        characterKit.def_max += 2586
                    case 13: # STR F2P
                        characterKit.hp_max += 2586
                        characterKit.atk_max += 3060
                        characterKit.def_max += 2346
                    case 14: # PHY F2P
                        characterKit.hp_max += 2826
                        characterKit.atk_max += 2820
                        characterKit.def_max += 2346
                    case 20: # AGL Summonable
                        characterKit.hp_max += 3910
                        characterKit.atk_max += 4700
                        characterKit.def_max += 4710
                    case 21: # TEQ Summonable
                        characterKit.hp_max += 3910
                        characterKit.atk_max += 5100
                        characterKit.def_max += 4310
                    case 22: # INT Summonable
                        characterKit.hp_max += 4310
                        characterKit.atk_max += 4700
                        characterKit.def_max += 4310
                    case 23: # STR Summonable
                        characterKit.hp_max += 4310
                        characterKit.atk_max += 5100
                        characterKit.def_max += 3910
                    case 24: # PHY Summonable
                        characterKit.hp_max += 4710
                        characterKit.atk_max += 4700
                        characterKit.def_max += 3910
                    case 30: # AGL Summonable (Old)
                        characterKit.hp_max += 5474
                        characterKit.atk_max += 6580
                        characterKit.def_max += 6594
                    case 31: # TEQ Summonable (Old)
                        characterKit.hp_max += 5474
                        characterKit.atk_max += 7140
                        characterKit.def_max += 6034
                    case 32: # INT Summonable (Old)
                        characterKit.hp_max += 6034
                        characterKit.atk_max += 6580
                        characterKit.def_max += 6034
                    case 33: # STR Summonable (Old)
                        characterKit.hp_max += 6034
                        characterKit.atk_max += 7140
                        characterKit.def_max += 5474
                    case 34: # PHY Summonable (Old)
                        characterKit.hp_max += 6594
                        characterKit.atk_max += 6580
                        characterKit.def_max += 5474
                    case _: # Special HiPo
                        characterKit.hp_max += 3448
                        characterKit.atk_max += 3760
                        characterKit.def_max += 3448
    
    if characterID >= 4000000:
        characterKit.name += (' (<->)')
            
    os.system('cls')
    return characterKit

def debugMain(dbCursor):
    dbCursor.execute(f'''SELECT * FROM cards''')
    cards = dbCursor.fetchall()
    for card in cards:
        if card[0] % 2 == 0:
            continue
        main(card[0], dbCursor)

def main():   
    if not idEntry.get():
        characterID = 0
    else:
        characterID = int(idEntry.get())     
    if not partneridEntry.get():
        partnerID = 0
    else:
        partnerID = int(partneridEntry.get())
    EZA = ezaEntry.get()
    
    if characterID == 0:
        debugMain(dbCursor)
        exit(0)
    else:
        mainUnit = getKit(characterID, dbCursor, EZA)
    
    dbCursor.execute(f'''SELECT * FROM leader_skill_sets where id = {mainUnit.leader_skill}''')
    dbOutput = dbCursor.fetchall()
    kitLabelText = f'{mainUnit.awakening_element_type} {mainUnit.element} {mainUnit.rarity} [{dbOutput[0][1]}] {mainUnit.name}\nLeader Skill: {dbOutput[0][2]}'
    
    for special in mainUnit.specials:
        dbCursor.execute(f'''SELECT * FROM special_sets where id = {special[0]}''')
        dbOutput = dbCursor.fetchall()[0]
        kitLabelText += f'\nSuper Attack: {dbOutput[1]} - {dbOutput[2]}'
        if special[2] != 0:
            dbCursor.execute(f'''SELECT * FROM special_bonuses where id = {special[2]}''')
            dbOutput = dbCursor.fetchall()[0]
            kitLabelText += f'- {dbOutput[2]}'
            if special[3] != 0:
                dbCursor.execute(f'''SELECT * FROM special_bonuses where id = {special[3]}''')
                dbOutput = dbCursor.fetchall()[0]
                kitLabelText += f'- {dbOutput[2]}'
    
    if mainUnit.passive_skill_set_id:
        dbCursor.execute(f'''SELECT * FROM passive_skill_sets where id = {mainUnit.passive_skill_set_id}''')
        dbOutput = dbCursor.fetchall()[0]
        kitLabelText += f'\nPassive Skill: {dbOutput[1]}\n{dbOutput[2]}'
    
    if mainUnit.costumes:
        kitLabelText += f'\nCostume: {mainUnit.costumes}'
    
    #if mainUnit.dokkan_fields:
    #    kitLabelText += f'\nDomain Skill: {mainUnit.dokkan_fields[0]}\n- {mainUnit.dokkan_fields[1]}'
    
    if mainUnit.active_skill_set_id:
        dbCursor.execute(f'''SELECT * FROM active_skill_sets where id = {mainUnit.active_skill_set_id}''')
        dbOutput = dbCursor.fetchall()[0]
        kitLabelText += f'\nActive Skill: {dbOutput[1]}\n- Effect: {dbOutput[2]}\n- Condition: {dbOutput[3]}'
        
    if mainUnit.standby_skills:
        kitLabelText += f'\nStandby Skill: {mainUnit.standby_skills[0]}\n- Effect: {mainUnit.standby_skills[1]}\n- Condition: {mainUnit.standby_skills[2]}'
        
    for finish_skill in mainUnit.finish_skills:
        kitLabelText += f'\nFinish Skill: {finish_skill[0]}\n- Effect: {finish_skill[1]}\n- Condition: {finish_skill[2]}'
    
    print('\nLink Skills:')
    for card_link in mainUnit.card_links:
        if not card_link:
            break
        dbCursor.execute(f'''SELECT * FROM link_skills WHERE id = {card_link}''')
        dbOutput = dbCursor.fetchall()[0]
        print(f'- {dbOutput[1]}')
    
    print(f'\nCategories:')
    dbCursor.execute(f'''SELECT * FROM card_card_categories where card_id = {characterID}''')
    dbOutput = dbCursor.fetchall()
    for category in dbOutput:
        dbCursor.execute(f'''SELECT * FROM card_categories where id = {category[2]}''')
        dbOutput = dbCursor.fetchall()[0][1]
        mainUnit.categories.append(dbOutput)
    print(mainUnit.categories)
    
    print('\nStats: ')
    print(f'HP: {mainUnit.hp_max} | ATK: {mainUnit.atk_max} | DEF: {mainUnit.def_max}')
    
    #kitLabel = tk.Label(root, text=kitLabelText)
    #kitLabel.grid(row=0, column=1, padx=5, pady=5)
    
    if not mainUnit.card_links:
        print("No partners available.")
        calculateLinks(mainUnit, mainUnit, dbCursor)
    else:
        if partnerID == characterID or not partnerID:
            calculateLinks(mainUnit, mainUnit, dbCursor)
        else:
            partnerKit = getPartnerKit(int(partnerID))
            calculateLinks(mainUnit, partnerKit, dbCursor)
    
    #if mainUnit.transformation:
    #    input(f'Click any button to continue with transformed form:')
    #    main(mainUnit.transformation, dbCursor)

os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
dbConnect = sqlite3.connect('database.db')
dbCursor = dbConnect.cursor()

# Create the main window
root = tk.Tk()
root.title("Manila's Dokkan Calculator")
root['background'] ='#353A40'

# Create labels for images
mainPic = PhotoImage(file="TeamBaseEmpty.png")
partnerPic = PhotoImage(file="TeamBaseEmpty.png")
mainLabel = tk.Label(root, highlightbackground='#222222', highlightthickness=5, image=mainPic)
partnerLabel = tk.Label(root, highlightbackground='#222222', highlightthickness=5, image=partnerPic)

# Create a label for text
kitLabel = tk.Label(root, wraplength=500) # wraplength for text wrapping

# Place widgets using the grid layout manager
mainLabel.grid(row=0, column=0, padx=5, pady=5)
kitLabel.grid(row=0, column=1, padx=5, pady=5)
partnerLabel.grid(row=0, column=2, padx=5, pady=5)

# Create the Entry widget
idLabel = tk.Label(root, highlightbackground='#555555', highlightthickness=5, text="Enter unit ID:")
idLabel.grid(row=1, column=0, padx=5, pady=5)
idEntry = tk.Entry(root, highlightbackground='#555555', highlightthickness=5, width=10)
idEntry.grid(row=2, column=0, padx=5, pady=5)

# Create the Entry widget
partneridLabel = tk.Label(root, text="Enter partner ID:")
partneridLabel.grid(row=1, column=2, padx=5, pady=5)
partneridEntry = tk.Entry(root, width=10)
partneridEntry.grid(row=2, column=2, padx=5, pady=5)

# Create a Tkinter variable to hold the selected radio button value
ezaEntry = tk.IntVar()
ezaEntry.set(0)  # Set an initial selected value
baseLabel = tk.Radiobutton(root, text="Base", variable=ezaEntry, value=0)
baseLabel.grid(row=3, column=0, padx=5, pady=5)
ezaLabel = tk.Radiobutton(root, text="EZA", variable=ezaEntry, value=1)
ezaLabel.grid(row=3, column=1, padx=5, pady=5)
sezaLabel = tk.Radiobutton(root, text="SEZA", variable=ezaEntry, value=2)
sezaLabel.grid(row=3, column=2, padx=5, pady=5)

# Create the first radio button and place it in column 0
hipoEntry = tk.IntVar()
hipoEntry.set(5)  # Set an initial selected value
hipoLabel1 = tk.Radiobutton(root, text="0%", variable=hipoEntry, value=0)
hipoLabel1.grid(row=4, column=0, padx=5, pady=5)
hipoLabel2 = tk.Radiobutton(root, text="55%", variable=hipoEntry, value=1)
hipoLabel2.grid(row=4, column=1, padx=5, pady=5)
hipoLabel3 = tk.Radiobutton(root, text="69%", variable=hipoEntry, value=2)
hipoLabel3.grid(row=4, column=2, padx=5, pady=5)
hipoLabel4 = tk.Radiobutton(root, text="79%", variable=hipoEntry, value=3)
hipoLabel4.grid(row=5, column=0, padx=5, pady=5)
hipoLabel5 = tk.Radiobutton(root, text="90%", variable=hipoEntry, value=4)
hipoLabel5.grid(row=5, column=1, padx=5, pady=5)
hipoLabel6 = tk.Radiobutton(root, text="100%", variable=hipoEntry, value=5)
hipoLabel6.grid(row=5, column=2, padx=5, pady=5)

domain = tk.IntVar()
domain.set(0)  # Set an initial selected value
domainLabel = tk.Checkbutton(root, text="Domain", variable=domain)
domainLabel.grid(row=6, column=0, padx=5, pady=5)

gogeta = tk.IntVar()
gogeta.set(0)  # Set an initial selected value
gogetaLabel = tk.Checkbutton(root, text="LR Gogeta Active Support (ATK & DEF +54% and attacks effective against all Types)", variable=gogeta)
gogetaLabel.grid(row=6, column=1, padx=5, pady=5)

active = tk.IntVar()
active.set(0)  # Set an initial selected value
activeLabel = tk.Checkbutton(root, text="Active", variable=active)
activeLabel.grid(row=6, column=2, padx=5, pady=5)

# Button to trigger the function
entryButton = tk.Button(root, text="Calculate", command=main)
entryButton.grid(row=7, column=1, padx=5, pady=5)

# Button for closing
exitButton = Button(root, text="Exit", command=root.destroy)
exitButton.grid(row=10, column=1, padx=5, pady=5)

root.mainloop()