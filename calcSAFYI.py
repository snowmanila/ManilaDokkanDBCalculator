import requests
import os
import time
import copy

from dataclasses import dataclass

# Class for keeping track of a unit and its kit
@dataclass
class Unit:
    id: int
    unitClass: str
    type: str
    rank: str
    title: str
    name: str
    lead: str
    SANames: list
    SAEffects: list
    passiveName: str
    passive: str
    links: list
    linkBuffs: list
    categories: list
    stats: list
    kiValues: list
    kiMultiplier: int
    transform: int 
    
    def __init__(self, id, unitClass, type, rank, title, name, lead, SANames, 
    SAEffects, passiveName, passive, links, linkBuffs, categories, stats, 
    kiValues, kiMultiplier, transform):
        self.id = id
        self.unitClass = unitClass
        self.type = type
        self.rank = rank
        self.title = title
        self.name = name
        self.lead = lead
        self.SANames = SANames
        self.SAEffects = SAEffects
        self.passiveName = passiveName
        self.passive = passive
        self.links = links
        self.linkBuffs = linkBuffs
        self.categories = categories
        self.stats = stats
        self.kiValues = kiValues
        self.kiMultiplier = kiMultiplier
        self.transform = transform
        
# Class for keeping track of a linking partner
@dataclass
class Partner:
    id: int
    type: str
    rank: str
    name: str
    links: list
    
    def __init__(self, id, type, rank, name, links):
        self.id = id
        self.type = type
        self.rank = rank
        self.name = name
        self.links = links
        
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # Reference to the next node

# LinkedList class manages the nodes and operations of the linked list
class LinkedList:
    def __init__(self):
        self.head = None  # Initialize an empty linked list
        
    def insertLine(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node
        
    def removeLine(self):
        if (self.head == None):
            return
        
        self.head = self.head.next

# Dev Note: Distinguish links to not be calculated SoT
    # - Berserker - ATK +30% when HP is 50% or less
    # - Revival - Ki +2; ATK & DEF +5% and recovers 5% HP when HP is 50% or less
    # - Dodon Ray - ATK +15% when performing a Super Attack
    # - Kamehameha - ATK +10% when performing a Super Attack
    # - Warrior Gods - ATK +10%; plus an additional ATK +5% when performing a Super Attack
    # - Power Bestowed by God - ATK +10% when performing a Super Attack
    # - Limit-Breaking Form - ATK +10% when performing a Super Attack
    # - Legendary Power - ATK +15% when performing a Super Attack
    
# Dev To-Do:
    # - 

# Retrieve leader skill
def retrieveLead(response, rank, EZA):
    lead = response[response.find('. | ')+4:response.find('name="description"')-2]
    if EZA == "1" or EZA == "2":
        i = 0
        while response.__contains__('leader_skill'):
            response = response[response.find('leader_skill')+12:]
            i += 1
        
            if rank == 'UR' and i == 8:
                break
            elif rank == 'LR' and i == 2:
                break
        lead = response[response.find('description&quot;:&quot;')+24:response.find('&quot;,&quot;effects')]            

    lead = lead.replace("\&quot;", "'")
    lead = lead.replace("&#39;", "'")
    lead = lead.replace("&amp;", "&")
    lead = lead.replace("+ ", "+")
    
    return lead

# Retrieve name of Super Attack
def retrieveSA(response, rank, EZA):
    if rank == 'LR':
        kiMultiplier = response[response.find('12,&quot;multiplier&quot;:')+26:response.find('},&quot;max')]
    else:
        kiMultiplier = response[response.find('12,&quot;multiplier&quot;:')+26:response.find('}},&quot;leader_skill')]
    SAContent = response[response.find('super_atks'):response.find('],&quot;passive_skill&quot;')]
    
    SANames = []
    SAEffects = []
    kiValues = []
    i = 0
    while SAContent.__contains__("secondary_effects"):
        SAContent = SAContent[SAContent.find(',&quot;name&quot;:&quot;')+24:]
        
        SAName = SAContent[:SAContent.find('&quot;,&quot;description')]
        if SAName.__contains__(',&quot;name&quot;:&quot;'):
            SAName = SAName[SAName.find(',&quot;name&quot;:&quot;')+24:]
        SAName = SAName.replace("\\n", "")
        SAName = SAName.replace("&amp;", "&")
        SAName = SAName.replace("&#39;", "'")
        SAName = SAName.replace("&quot;", "")
        
        SAContent = SAContent[SAContent.find('&quot;,&quot;description&quot;:&quot;')+37:]
        SAEffect = SAContent[:SAContent.find('&quot;,&quot;effects')]
        if SAEffect.__contains__(',&quot;description&quot;:&quot;'):
            SAEffect = SAEffect[SAEffect.find(',&quot;description&quot;:&quot;')+31:]
        
        if SAContent.__contains__("secondary_effects&quot;:[{"):
            SAContent = SAContent[SAContent.find(',&quot;name&quot;:&quot;')+24:]
            effect = SAContent[:SAContent.find('&quot;,&quot;description&quot;:&quot;')]
            
            if effect == "Super Attack Transformation ":
                effect = SAContent[SAContent.find('&quot;,&quot;description&quot;:&quot;')+37:SAContent.find('&quot;,&quot;lv&quot;:')]
            if not effect.__contains__(',&quot;name&quot;:&quot;'):
                SAEffect += f" ({effect})"
        SAEffect = SAEffect.replace("\\n", "")
        SAEffect = SAEffect.replace("&amp;", "&")
        SAEffect = SAEffect.replace("&#39;", "'")
        SAEffect = SAEffect.replace("&quot;", "")
        SAEffect = SAEffect.replace(" )", ")")
        
        SAContent = SAContent[SAContent.find(';ki&quot;:')+10:]
        kiValue = SAContent[:SAContent.find(',&quot;lv')]
        
        if SAEffect.__contains__('Required Ki -'):
            subKi = SAEffect.split('Required Ki -')[1]
            subKi = int(subKi.split(' for launching Super')[0])
            kiValue = str(int(kiValue) - subKi)
        
        if (EZA == '1' or EZA == '2') and SAName.__contains__('(Extreme)'):
            SANames[i] = SAName
            SAEffects[i] = SAEffect
            kiValues[i] = kiValue
            i += 1
        elif SAName.__contains__('(Extreme)'):
            return SANames, SAEffects, kiValues, kiMultiplier
        else:
            SANames.append(SAName)
            SAEffects.append(SAEffect)
            kiValues.append(int(kiValue))
        
        SAContent = SAContent[SAContent.find("},{&quot;id&quot;:")+17:]
    return SANames, SAEffects, kiValues, kiMultiplier

# Retrieve name of Passive Skill
def retrievePassive(response, rank, EZA):
    response = response[response.find('passive_skill'):]
    
    if response.__contains__('passive_skill&quot;:null'):
        return 'None', '- None'
    
    passiveName = response[response.find(',&quot;name&quot;:&quot;')+24:response.find('&quot;,&quot;description&quot;')]
    passiveName = passiveName.replace("&#39;", "'")
    
    if EZA == '1':
        i = 0
        while response.__contains__('description_itemized'):
            response = response[response.find('description_itemized')+20:]
            i += 1
        
            if rank == 'UR' and i == 8:
                break
            elif rank == 'LR' and i == 4:
                break
    elif EZA == '2':
        i = 0
        while response.__contains__('description_itemized'):
            response = response[response.find('description_itemized')+20:]
        
            if rank == 'UR' and i == 8:
                print(response[:1000])
                time.sleep(3)
            elif rank == 'LR' and i == 4:
                print(response[:1000])
                time.sleep(3)
                
    response = response[response.find('[{&quot;description&quot;:&quot;')+1:]
    passive = response[:response.find('&quot;]}],&quot;')]
    
    passive = passive.replace('{&quot;description&quot;:&quot;', "*")
    passive = passive.replace('&quot;,&quot;effects&quot;:', ":\n")
    passive = passive.replace('[&quot;', '- ')
    passive = passive.replace('&quot;,&quot;', '\n- ')
    passive = passive.replace('&quot;]},','\n\n')
    passive = passive.replace("\\n", "")
    passive = passive.replace("&amp;", "&")
    passive = passive.replace("&#39;", "'")
    passive = passive.replace("&quot;", "")
    passive = passive.replace("\\", "'")
    passive = passive.replace("  ", " ")
    
    passive = passive.replace("granting deadly power to attack", "ATK +1000000%")
    passive = passive.replace(" (count starts from the ", ", starting from the ")
    passive = passive.replace(" in the following status: ", " ")
    passive = passive.replace("{passiveImg:atk_down}", "in ATK Down status")
    passive = passive.replace("{passiveImg:def_down}", "in DEF Down status")
    passive = passive.replace("{passiveImg:stun}", "Stunned")
    passive = passive.replace("{passiveImg:astute}", "Sealed")

    return passiveName, passive

# Retrieve Linkset
def retrieveLinks(response):
    response = response[response.find('link_skills&quot'):]

    links = []
    linkBuffs = []
    while response.__contains__("lv&quot;:10"):
        response = response[response.find('&quot;name&quot;:&quot;')+23:]
        link = response[:response.find('&quot;,&quot;')]
        link = link.replace("\\n", "")
        link = link.replace("&amp;", "&")
        link = link.replace("&#39;", "'")
        link = link.replace("&quot;", "")
        links.append(link)
        
        response = response[response.find('lv&quot;:10')+42:]
        linkBuff = response[:response.find('&quot;}]}')]
        linkBuff = linkBuff.replace("\\n", "")
        linkBuff = linkBuff.replace("&amp;", "&")
        linkBuff = linkBuff.replace("&#39;", "'")
        linkBuff = linkBuff.replace("&quot;", "")
        linkBuffs.append(linkBuff)

    return links, linkBuffs

# Retrieve Categories of unit
def retrieveCategories(response):   
    response = response[response.find('],&quot;categories'):response.find('support&quot;:[]}}],&quot;a')]
    if response.__contains__('categories&quot;:[]'):
        return []

    categories = []
    while response.__contains__("&quot;name&quot;:&quot;"):
        response = response[response.find('&quot;name&quot;:&quot;')+23:]
        category = response[:response.find('&quot;,&quot;characters')]
        category = category.replace("&#39;", "'")
        
        categories.append(category)

    return categories

# Retrieve HP, ATK, and DEF stats of unit
def retrieveStats(response, characterID, EZA, rank):       
    response = response[response.find(',&quot;hp&quot;:'):]   
    stats = []
    
    response = response[response.find(',&quot;max&quot;:')+17:] 
    hpMax = int(response[:response.find(',&quot;eza&quot;:')])
    response = response[response.find(',&quot;eza&quot;:')+17:]
    hpEZA = int(response[:response.find('},')])
    stats.append(hpMax)
    
    response = response[response.find(',&quot;max&quot;:')+17:] 
    atkMax = int(response[:response.find(',&quot;eza&quot;:')])
    response = response[response.find(',&quot;eza&quot;:')+17:]
    atkEZA = int(response[:response.find('},')])
    stats.append(atkMax)
    
    response = response[response.find(',&quot;max&quot;:')+17:] 
    defMax = int(response[:response.find(',&quot;eza&quot;:')])
    response = response[response.find(',&quot;eza&quot;:')+17:]
    defEZA = int(response[:response.find('},')])
    stats.append(defMax)
    
    if EZA != '0' and rank != 'LR':
        stats[0] = hpEZA
        stats[1] = atkEZA
        stats[2] = defEZA

    if not response.__contains__('hidden_potential&quot;:null'):
        response = response[response.find('hidden_potential&quot;:'):]

        response = response[response.find('&quot;hp&quot;:')+15:]
        hpHIPO = int(response[:response.find(',&quot;atk&quot;:')])
        stats[0] += hpHIPO
        
        response = response[response.find(',&quot;atk&quot;:')+17:] 
        atkHIPO = int(response[:response.find(',&quot;def&quot;:')])
        stats[1] += atkHIPO
        
        response = response[response.find(',&quot;def&quot;:')+17:] 
        defHIPO = int(response[:response.find('}')])
        stats[2] += defHIPO
    elif rank == "SSR" or rank == "UR" or rank == "LR":
        response = response[response.find('base_character_id&quot;:1011351')+24:]
        originID = response[:response.find(',&quot;base_character')]
        
        originResponse = (requests.get(f'https://dokkan.fyi/characters/{originID}')).text
        originResponse = originResponse[originResponse.find('hidden_potential&quot;:'):]

        originResponse = originResponse[originResponse.find('&quot;hp&quot;:')+15:]
        hpHIPO = int(originResponse[:originResponse.find(',&quot;atk&quot;:')])
        
        originResponse = originResponse[originResponse.find(',&quot;atk&quot;:')+17:] 
        atkHIPO = int(originResponse[:originResponse.find(',&quot;def&quot;:')])
        
        originResponse = originResponse[originResponse.find(',&quot;def&quot;:')+17:] 
        defHIPO = int(originResponse[:originResponse.find('}')])
        
        response = response[response.find(f'&quot;id&quot;:{characterID}')+15:]

        response = response[response.find(',&quot;max&quot;:')+17:]
        hpMax = response[:response.find('},&quot;atk&quot;:{')]
        if not EZA == '0':
            hpMax = int(hpMax[:hpMax.find(',&quot;eza&quot;:')])
        else:
            hpMax = int(hpMax[hpMax.find(',&quot;eza&quot;:')+17:])
        stats[0] = hpMax + hpHIPO
            
        response = response[response.find(',&quot;max&quot;:')+17:]
        atkMax = response[:response.find('},&quot;atk&quot;:{')]
        if not EZA == '0':
            atkMax = int(atkMax[:atkMax.find(',&quot;eza&quot;:')])
        else:
            atkMax = int(atkMax[atkMax.find(',&quot;eza&quot;:')+17:])
        stats[1] = atkMax + atkHIPO
            
        response = response[response.find(',&quot;max&quot;:')+17:]
        defMax = response[:response.find('},&quot;atk&quot;:{')]
        if not EZA == '0':
            defMax = int(defMax[:defMax.find(',&quot;eza&quot;:')])
        else:
            defMax = int(defMax[defMax.find(',&quot;eza&quot;:')+17:])
        stats[2] = defMax + defHIPO

    return stats

# Calculate ATK stat given 'on attack' conditions (When attacking, per attack
# evaded/received/performed, when the target enemy ..., etc.)
def calcATKSA(ki, SAName, SAEffect, ATK, onAttackATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional):      
    copyATK = copy.copy(onAttackATK)
    if (copyATK.head != None):
        condition = f'({(copyATK.head.data).split(" (")[1]}'
        buff = f'({(copyATK.head.data).split(" (")[0]}'
        
        if buff.__contains__('counter') or buff.__contains__('Counter'):
            counter = buff
            copyATK.removeLine()
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            return
        else:
            newSAPerBuff = saPerBuff
            newSAFlatBuff = saFlatBuff
            buff = buff.split("ATK ")[1]
        
            if (copyATK.head.data).__contains__("(up to "):
                limit = (copyATK.head.data).split("(up to ")[1]
                limit = int(limit.split("%)")[0])
            
            flat = False
            if '%' not in buff:
                flat = True
            else:
                flat = False
                buff = buff.split("%")[0]
            
            if '+' in buff:
                buff = int(buff.split('+')[1])
            else:
                buff = -1*int(buff.split('-')[1])
            
            if flat:
                newSAFlatBuff += buff
            else:
                newSAPerBuff += buff
        
        copyATK.removeLine()
        if (condition.__contains__("After delivering a final blow") or
            condition.__contains__("a final blow is delivered")):
            print("ATK (Before delivering a final blow):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif (condition.__contains__("When attacking a") and
        condition.__contains__(" enemy")):
            print(f"ATK {condition}")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            condition = condition.replace('When attacking a', 'When not attacking a')
            print(f"ATK {condition}")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif (condition.__contains__("When there is a") and
        condition.__contains__(" enemy")):
            print(f"ATK {condition}")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            condition = condition.replace('When there is a', 'When there is not a')
            print(f"ATK {condition}")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("receiving an attack"):
            print("ATK (Before receiving an attack):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__('After guard is activated'):
            print('ATK (Before guard is activated):')
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print(f'ATK {condition}:')
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every attack evaded"):
            for i in range(0, int(limit/buff)+1):
                print("ATK (With " + str(i) + " attacks evaded):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i), saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every attack performed"):
            for i in range(1, int(limit/buff)+1):
                if i == 1:
                    print("ATK (With " + str(i) + " attack performed):")
                else:
                    print("ATK (With " + str(i) + " attacks performed):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i), saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every Super Attack performed"):
            for i in range(1, int(limit/buff)+1):
                print("ATK (With " + str(i) + " Super Attacks performed):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i), saFlatBuff, counter, crit, superEffective, additional)
            if limit % buff != 0:
                print("ATK (With " + str(i+1) + " Super Attacks performed):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i) + (limit % buff), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i) + (limit % buff), saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every attack received or evaded"):
            for i in range(0, int(limit/buff)+1):
                if i == 1:
                    print("ATK (With " + str(i) + " attack received or evaded):")
                else:
                    print("ATK (With " + str(i) + " attacks received or evaded):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i), saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every attack received"):
            for i in range(0, int(limit/buff)+1):
                if i == 1:
                    print("ATK (With " + str(i) + " attack received):")
                else:
                    print("ATK (With " + str(i) + " attacks received):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (buff*i), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (buff*i), saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("When facing") and condition.__contains__("enem"):
            print(f'ATK {condition}:')
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            
            condition = condition.replace('hen ', 'hen not ')
            
            print(f'ATK {condition}:')
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("Category ally attacking in the same turn"):
            category = condition.split("Per '")[1]
            category = category.split("' Category")[0]
                
            if condition.__contains__("self excluded"): 
                for i in range(0, 3):
                    print("ATK (With " + str(i) + " " + category + " Category allies in the same turn) (When attacking):")
                    calcATKSA(ki, SAName, SAEffect, ATK * (1 + (i * (buff/100))), copyATK, counter, crit, superEffective, additional)
            else:
                for i in range(1, 4):
                    print("ATK (With " + str(i) + " " + category + " Category allies in the same turn) (When attacking):")
                    calcATKSA(ki, SAName, SAEffect, ATK * (1 + (i * (buff/100))), copyATK, counter, crit, superEffective, additional)
        elif condition.__contains__("Starting from the ") and condition.__contains__(" turn from the "):
            print("ATK (" + condition + ":")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("turn(s)"):
            print("ATK (" + condition + ":")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            print("ATK (After turn buff):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("When the target enemy is "):
            condition = condition.replace("{passiveImg:atk_down}", "ATK Down")
            condition = condition.replace("{passiveImg:def_down}", "DEF Down")
            condition = condition.replace("{passiveImg:stun}", "Stunned")
            condition = condition.replace("{passiveImg:astute}", "Sealed")
            
            print("ATK (Without status condition):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print("ATK (" + condition + ":")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("After performing ") and condition.__contains__("ttack(s) in battle"):
            cond = condition.split("After performing ")[1]
            
            print(f"ATK (Before performing {cond}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print(f"ATK (After performing {cond}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("After receiving ") and condition.__contains__("ttacks in battle"):
            cond = condition.split("After receiving ")[1]
            
            print(f"ATK (Before receiving {cond}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            print(f"ATK (After receiving {cond}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("For every Ki when attacking"):
            if limit/buff <= ki:
                print(f"ATK (With 12 Ki):")
                calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            else:
                print(f"ATK (Before performing {cond}):")
                #calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
                #print(f"ATK (After performing {cond}):")
                #calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__(" your team has ") and condition.__contains__("attacking in the same turn"):
            cond = condition.split(" your team has ")[0]
            ally = condition.split("your team has ")[1]
            
            print(f"ATK ({cond} your team has {ally}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            print(f"ATK ({cond} your team doesn't have {ally}):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("Ki Spheres obtained"):
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            
            condition = condition.replace(' obtained,', ' not obtained,')
            
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("chance") or condition.__contains__("Chance"):
            condition = condition.replace('hance', 'hance to activate')
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            print("ATK (Without RNG chance):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif (condition.__contains__("Per ") and condition.__contains__(" ally on the team")):
            category = condition.split("Per ")[1]
            category = category.split(" ally")[0]
            
            limitLoop = 8
            if "limit" in locals(): # WE SAIYANS-
                limitLoop = int(limit/buff)+1
            for i in range(1, limitLoop):
                print("ATK (With " + str(i) + " " + category + " allies on the team):")
                if flat:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff + (i * buff), counter, crit, superEffective, additional)
                else:
                    calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff + (i * buff), saFlatBuff, counter, crit, superEffective, additional)
        elif (condition.__contains__("When there is a") and condition.__contains__(" ally on the team")):
            ally = condition.split("When there is a")[1]
            ally = ally.split(" ally")[0]
            
            print("ATK (With a" + ally + " ally on the team):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
            print("ATK (Without a" + ally + " ally on the team):")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
        elif condition.__contains__("When attacking with ") and condition.__contains__(" Ki"):
            kiATK = condition.split("When attacking with ")[1]
            kiATK = int(kiATK.split(" ")[0])
            if ((condition.__contains__("or more") and int(ki) < kiATK) or
            (condition.__contains__("or less") and int(ki) > kiATK)):
                calcATKSA(ki, SAName, SAEffect, ATK, copyATK, saPerBuff, saFlatBuff, counter, crit, superEffective, additional)
            else:
                print(f"ATK {condition}:")
                calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
        else:
            print(f"ATK {condition}:")
            calcATKSA(ki, SAName, SAEffect, ATK, copyATK, newSAPerBuff, newSAFlatBuff, counter, crit, superEffective, additional)
    else:
        ATK = int(ATK * (1 + (saPerBuff/100))) # Apply 'on attack' percentage buffs
        print(f"{ATK} (With {saPerBuff}% 'On Attack' Passive Buff)")
        ATK = int(ATK + saFlatBuff) # Apply 'on attack' flat buffs
        print(f"{ATK} (With {saFlatBuff} Flat 'On Attack' Passive Buff)")
        
        ATKmultiplier = 0
        if (SAEffect.__contains__(", allies' ATK +") or
        SAEffect.__contains__("; allies' ATK +") or
        SAEffect.__contains__(", allies' ATK & DEF +") or
        SAEffect.__contains__("; allies' ATK & DEF +") or
        SAEffect.__contains__("and allies' ATK +") or
        SAEffect.__contains__("and allies' ATK & DEF +")):
            buff = SAEffect.split("+")[1]
            buff = int(buff.split("%")[0])
            ATKmultiplier = ATKmultiplier + (buff/100)
        elif (SAEffect.__contains__("allies' ATK by ") or
        SAEffect.__contains__("allies' ATK & DEF by ")):
            buff = SAEffect.split("by ")[1]
            buff = int(buff.split("%")[0])
            ATKmultiplier = ATKmultiplier + (buff/100)
        elif (SAEffect.__contains__("ATK +") and
        SAEffect.__contains__("for all allies")):
            ATKmultiplier = ATKmultiplier + (int(SAEffect[SAEffect.find("ATK +")+5:SAEffect.find("%")])/100)
            
        stack = False
        if (SAEffect.__contains__("Massively raises ATK and ") or
        SAEffect.__contains__("Massively raises ATK, ") or
        SAEffect.__contains__("Massively raises ATK & DEF and ") or
        SAEffect.__contains__("Massively raises ATK & DEF, ")):
            stack = True
            ATKmultiplier = ATKmultiplier + 1
        elif (SAEffect.__contains__("Massively raises ATK") 
            or SAEffect.__contains__("Massively raises ATK & DEF")):
            ATKmultiplier = ATKmultiplier + 1
        elif ((SAEffect.__contains__("Greatly raises ATK and ") or
        SAEffect.__contains__("Greatly raises ATK, ") or
        SAEffect.__contains__("Greatly raises ATK & DEF and ") or
        SAEffect.__contains__("Greatly raises ATK & DEF,")) and
        not SAEffect.__contains__("Greatly raises ATK and raises DEF for 1 turn")):
            stack = True
            ATKmultiplier = ATKmultiplier + .5
        elif (SAEffect.__contains__("Greatly raises ATK by 67% and ") or
        SAEffect.__contains__("Greatly raises ATK by 67%, ")):
            stack = True
            ATKmultiplier = ATKmultiplier + .67
        elif (SAEffect.__contains__("Greatly raises ATK") or
        SAEffect.__contains__("Greatly raises ATK & DEF")):
            ATKmultiplier = ATKmultiplier + .5
        elif (SAEffect.__contains__("Raises ATK and ") or
        SAEffect.__contains__("Raises ATK, ")):
            stack = True
            ATKmultiplier = ATKmultiplier + .3
        elif (SAEffect.__contains__("Raises ATK & DEF and ") or
        SAEffect.__contains__("Raises ATK & DEF, ")):
            stack = True
            ATKmultiplier = ATKmultiplier + .2
        elif (SAEffect.__contains__("Raises ATK for 1 turn") or
        SAEffect.__contains__("Raises ATK & DEF for 1 turn")):
            ATKmultiplier = ATKmultiplier + .3
        elif (SAEffect.__contains__("aises ATK for ") 
            or SAEffect.__contains__("aises ATK & DEF for ")):
            ATKmultiplier = ATKmultiplier + .5
        elif (SAEffect.__contains__("aises ATK by ") 
            or SAEffect.__contains__("aises ATK & DEF by ")):
            multiplier = SAEffect.split("by ")[1]
            multiplier = int(multiplier.split("%")[0])/100
            ATKmultiplier = ATKmultiplier + multiplier
            
        SAmultiplier = 2.6 # Damage by default
        if (SAEffect.__contains__("low damage") or
        SAEffect.__contains__("Low damage")):
            SAmultiplier = 2.2
        elif (SAEffect.__contains__("huge damage") or
        SAEffect.__contains__("Huge damage") or
        SAEffect.__contains__("destructive damage") or
        SAEffect.__contains__("Destructive damage")):
            SAmultiplier = 2.9
        elif (SAEffect.__contains__("extreme damage") or
        SAEffect.__contains__("Extreme damage") or
        SAEffect.__contains__("mass damage") or
        SAEffect.__contains__("Mass damage")):
            SAmultiplier = 3.55
        elif (SAEffect.__contains__("supreme damage") or
        SAEffect.__contains__("Supreme damage")):
            if SAName.__contains__("(Extreme)"):
                SAmultiplier = 5.3
            else:
                SAmultiplier = 4.3
        elif (SAEffect.__contains__("immense damage")):
            if SAName.__contains__("(Extreme)"):
                SAmultiplier = 6.3
            else:
                SAmultiplier = 5.05
        elif (SAEffect.__contains__("mega-colossal damage")):
            if SAName.__contains__("(Extreme)"):
                SAmultiplier = 5.9
            else:
                SAmultiplier = 5.4
        elif (SAEffect.__contains__("colossal damage")):
            if SAName.__contains__("(Extreme)"):
                SAmultiplier = 4.2
            else:
                SAmultiplier = 3.95
            
        if (SAEffect.__contains__("(Super Attack power +") or
            SAEffect.__contains__("(Super Attack +")):
            SAPower = SAEffect.split("(Super Attack ")[1]
            SAPower = SAPower.split("+")[1]
            SAPower = (int(SAPower.split("%")[0]))/100
            SAmultiplier = SAmultiplier + SAPower
            
        if SAEffect.__contains__('critical Hit'):
            crit = True
        
        print(f'Raises ATK by {ATKmultiplier}% with {SAmultiplier}% SA Multiplier')
        
        if counter != "":
            if counter.__contains__("enormous power"):
                counterPower = 2
            elif counter.__contains__("tremendous power"):
                counterPower = 3
            elif counter.__contains__("ferocious power"):
                counterPower = 4
        
        if (SAEffect.__contains__("% chance of Super Attack transforming for greater power!)")):
            if crit:
                print(f"Transformed Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier+.6)))} (Crit: {str(int(ATK*(ATKmultiplier+SAmultiplier+.6)*1.9))})")
                print(f"Normal Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier)))} (Crit: {str(int(ATK*(ATKmultiplier+SAmultiplier)*1.9))})")
            elif superEffective:
                print(f"Transformed Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier+.6)))} (Super Effective: {str(int(ATK*(ATKmultiplier+SAmultiplier+.6)*1.5))})")
                print(f"Normal Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier)))} (Super Effective: {str(int(ATK*(ATKmultiplier+SAmultiplier)*1.5))})")
            else:
                print(f"Transformed Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier+.6)))}")
                print(f"Normal Super Attack APT: {str(int(ATK*(ATKmultiplier+SAmultiplier)))}")
        elif stack:
            for i in range(1, 6+additional):
                stackATK = int(ATK*((ATKmultiplier*i)+SAmultiplier))
                if crit:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK) 
                    + " (Crit: " + str(int(stackATK*1.9)) + ")")
                elif superEffective:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK) 
                    + " (Super Effective: " + str(int(stackATK*1.5)) + ")")
                else:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK))
        elif (SAEffect.__contains__("raises ATK for 1 turn") and SAEffect.__contains__("raises DEF") and
        SAEffect.__contains__("turns")):
            finalATK = int(ATK*(SAmultiplier+ATKmultiplier))
            if crit:
                print("Super Attack APT: " + str(finalATK) + " (Crit: " + str(int(finalATK*1.9)) + ")")
            elif superEffective:
                print("Super Attack APT: " + str(finalATK) + " (Super Effective: " + str(int(finalATK*1.5)) + ")")
            else:
                print("Super Attack APT: " + str(finalATK))
        
            if additional != 0:
                for i in range(1, additional+1):
                    additionalATK = int(ATK*((SAmultiplier+(ATKmultiplier*(i+1)))))
                    if crit:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK) 
                            + " (Crit: " + str(int(additionalATK*1.9)) + ")")
                    elif superEffective:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK) 
                            + " (Super Effective: " + str(int(additionalATK*1.5)) + ")")
                    else:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK))
                        
                if counter != "":
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                    " (Crit: " + str(int(ATK*counterPower*1.9)) + ")")
                    
                    for i in range(1, additional+1):
                        print(f"Counter APT (After SA {i}): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                        " (Crit: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.9)) + ")")
                elif superEffective:
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                    " (Super Effective: " + str(int(ATK*counterPower*1.5)) + ")")
                    
                    for i in range(1, additional+1):
                        print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                        " (Super Effective: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.5)) + ")")
                else:
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): {str(int(ATK*counterPower))}")
                    
                    for i in range(1, additional+1):
                        print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): {str(int(ATK*(counterPower+(ATKmultiplier*i))))}")
            else:
                if counter != "":
                    if crit:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Crit: " + str(int(ATK*counterPower*1.9)) + ")")
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))) + 
                        " (Crit: " + str(int(ATK*(counterPower+ATKmultiplier)*1.9)) + ")")
                    elif superEffective:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Super Effective: " + str(int(ATK*counterPower*1.5)) + ")")
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))) + 
                        " (Super Effective: " + str(int(ATK*(counterPower+ATKmultiplier)*1.5)) + ")")
                    else:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)))
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))))
        elif ((SAEffect.__contains__("raises ATK") or SAEffect.__contains__("raises ATK & DEF")) and
        SAEffect.__contains__("turns")):
            turnLimit = SAEffect.split("ATK ")[1]
            turnLimit = turnLimit.split("for ")[1]
            turnLimit = int(turnLimit.split(" turns")[0])
            for i in range(1, turnLimit+additional+1):
                stackATK = int(ATK*((ATKmultiplier*i)+SAmultiplier))
                if crit:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK) 
                    + " (Crit: " + str(int(stackATK*1.9)) + ")")
                elif superEffective:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK) 
                    + " (Super Effective: " + str(int(stackATK*1.5)) + ")")
                else:
                    print("Super Attack APT (" + str(i) + " Stack): " + str(stackATK))
                
            if counter != "":
                if crit:
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                    " (Crit: " + str(int(ATK*counterPower*1.9)) + ")")
                    
                    for i in range(1, turnLimit+additional+1):
                        print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                        " (Crit: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.9)) + ")")
                elif superEffective:
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                    " (Super Effective: " + str(int(ATK*counterPower*1.5)) + ")")
                    
                    for i in range(1, turnLimit+additional+1):
                        print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                        " (Super Effective: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.5)) + ")")
                else:
                    print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): {str(int(ATK*counterPower))}")
                    
                    for i in range(1, turnLimit+additional+1):
                        print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): {str(int(ATK*(counterPower+(ATKmultiplier*i))))}")
        else:
            finalATK = int(ATK*(SAmultiplier+ATKmultiplier))
            if crit:
                print("Super Attack APT: " + str(finalATK) + " (Crit: " + str(int(finalATK*1.9)) + ")")
            elif superEffective:
                print("Super Attack APT: " + str(finalATK) + " (Super Effective: " + str(int(finalATK*1.5)) + ")")
            else:
                print("Super Attack APT: " + str(finalATK))
            
            if additional != 0:
                for i in range(1, additional+1):
                    additionalATK = int(ATK*((SAmultiplier+(ATKmultiplier*(i+1)))))
                    if crit:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK) 
                            + " (Crit: " + str(int(additionalATK*1.9)) + ")")
                    elif superEffective:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK) 
                            + " (Super Effective: " + str(int(additionalATK*1.5)) + ")")
                    else:
                        print("Super Attack APT (Additional " + str(i) + "): " + str(additionalATK))
                        
                if counter != "":
                    if crit:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Crit: " + str(int(ATK*counterPower*1.9)) + ")")
                        
                        for i in range(1, additional+1):
                            print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                            " (Crit: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.9)) + ")")
                    elif superEffective:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Super Effective: " + str(int(ATK*counterPower*1.5)) + ")")
                        
                        for i in range(1, additional+1):
                            print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+(ATKmultiplier*i)))) + 
                            " (Super Effective: " + str(int(ATK*(counterPower+(ATKmultiplier*i))*1.5)) + ")")
                    else:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): {str(int(ATK*counterPower))}")
                        
                        for i in range(1, additional+1):
                            print(f"Counter APT (After SA {i}, With {counterPower*100}% Multiplier): {str(int(ATK*(counterPower+(ATKmultiplier*i))))}")
            else:
                if counter != "":
                    if crit:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Crit: " + str(int(ATK*counterPower*1.9)) + ")")
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))) + 
                        " (Crit: " + str(int(ATK*(counterPower+ATKmultiplier)*1.9)) + ")")
                    elif superEffective:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)) + 
                        " (Super Effective: " + str(int(ATK*counterPower*1.5)) + ")")
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))) + 
                        " (Super Effective: " + str(int(ATK*(counterPower+ATKmultiplier)*1.5)) + ")")
                    else:
                        print(f"Counter APT (Before SA, With {counterPower*100}% Multiplier): " + str(int(ATK*counterPower)))
                        print(f"Counter APT (After SA, With {counterPower*100}% Multiplier): " + str(int(ATK*(counterPower+ATKmultiplier))))
        
        print()

def calcATKCond(characterKit, condSoTATK, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional):
    copyCond = copy.copy(condSoTATK)
    if (condSoTATK.head != None):
        if (condSoTATK.head.data).__contains__('ATK -'):
            buff = '-' + (copyCond.head.data).split("ATK -")[1]
        else:
            buff = (copyCond.head.data).split("ATK +")[1]
        buff = buff.split(" (")[0]
        
        condition = (copyCond.head.data)[(copyCond.head.data).find('('):]
        if not condition.__contains__(')'):
            condition += ')'
        
        if (condSoTATK.head.data).__contains__("(up to "):
            limit = (condSoTATK.head.data).split("(up to ")[1]
            limit = int(limit.split("%)")[0])

        '''if condition.__contains__("The more HP remaining"):
            buff = buff.split("(up to")[1]
            buff = buff.split(")")[0]
        else:
            if buff.__contains__("& DEF"):
                buff = buff.split("DEF ")[1]
            
            if buff.__contains__("{passiveImg:down_r}"):
                buff = "-" + buff
            buff = buff.split("{passiveImg:")[0]'''

        flat = False
        newPerBuff = atkPerBuff
        newFlatBuff = atkFlatBuff
        if '%' not in buff:
            flat = True
            newFlatBuff += int(buff)
        else:
            flat = False
            buff = buff.split('%')[0]
            newPerBuff += int(buff)
        
        copyCond.removeLine()
        
        if condition.__contains__("Once only") or condition.__contains__("once only"):
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)  
            print("ATK (After one-time buff):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)        
        elif condition.__contains__("for first attack only"):
            print("\nATK for first attack: ")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            print("\nATK after first attack: ")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("chance") or condition.__contains__("Chance"):
            condition = condition.replace('hance', 'hance to activate')
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            print("ATK (Without RNG chance):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__(", per Ki Sphere obtained"):
            cond1 = condition.split(', per')[0]            
            cond1 = cond1.replace('When there is ', 'When there is not ')
            print(f"ATK {cond1}):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            
            cond1 = cond1.replace('When there is not ', 'When there is ')
            if flat:
                if "limit" in locals():
                    print(f"ATK {cond1}, with {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (int(limit) * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK {cond1}, with 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                if "limit" in locals():
                    print(f"ATK {cond1}, with {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (int(limit)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK {cond1}, with 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("For every Ki Sphere obtained, "):
            cond1 = condition.split('obtained, ')[1]            
            cond1 = cond1.replace('when there is ', 'When there is not ')
            print(f"ATK ({cond1}:")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            
            cond1 = cond1.replace('When there is not ', 'When there is ')
            cond1 = cond1.replace('), ', ', ')
            if flat:
                if "limit" in locals():
                    print(f"ATK {cond1}, with {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (int(limit) * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK {cond1}, with 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                if "limit" in locals():
                    print(f"ATK {cond1}, with {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (int(limit)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK {cond1}, with 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK {cond1}, with 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("For every Ki Sphere obtained with "):
            kiStart = condition.split('obtained with ')[1]
            kiStart = int(kiStart.split(' or ')[0])
            print(f"ATK (With less than {kiStart} Ki Spheres Obtained):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            if flat:
                if "limit" in locals():
                    if int(limit/int(buff)) > 3:
                        print(f"ATK (With 3 Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (3 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                    if int(limit/int(buff)) >= 7.5:
                        print(f"ATK (With 7.5 (AVG) Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (7.5 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                    if int(limit/int(buff)) >= 23:
                        print(f"ATK (With 23 (Max) Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (23 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With {kiStart + int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + int(limit), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK (With {3 + kiStart} Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (3 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With {7.5 + kiStart} (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (7.5 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With {23 - kiStart} (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + ((23 - kiStart) * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                if "limit" in locals():
                    if int(limit/int(buff)) > 3:
                        print(f"ATK (With 3 Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    if int(limit/int(buff)) >= 7.5:
                        print(f"ATK (With 7.5 (AVG) Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    if int(limit/int(buff)) >= 23:
                        print(f"ATK (With 23 (Max) Ki Spheres Obtained):")
                        calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With {kiStart + int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + int(limit), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK (With 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("For every Ki Sphere obtained"):   
            if flat:
                if "limit" in locals():
                    print(f"ATK (With {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (23 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK (With 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                if "limit" in locals():
                    print(f"ATK (With {int(limit/int(buff))} (Max) Ki Spheres Obtained):")
                    print(int(65/3))
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (23 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    print(f"ATK (With 3 Ki Spheres Obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 7.5 (AVG) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                    print(f"ATK (With 23 (Max) Ki Spheres obtained):")
                    calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("For every Rainbow Ki Sphere obtained"):
            if flat:
                print("ATK (With 0 Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print("ATK (With 2.5 (AVG) Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (2.5 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                print("ATK (With 5 (Max) Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (5 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional) 
            else:
                print("ATK (With 0 Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print("ATK (With 2.5 (AVG) Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff + (2.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print("ATK (With 5 (Max) Rainbow Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff + (5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("For every ") and condition.__contains__(" Ki Sphere obtained"):
            kiType = (condition.split('For every ')[1]).split(' Ki Sphere')[0]
            if flat:
                print(f"ATK (With 0 {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 3 {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (3 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 7.5 (AVG) {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (7.5 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 23 (Max) {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (23 * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                print(f"ATK (With 0 {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 3 {kiType} Ki Spheres Obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff + (3 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 7.5 (AVG) {kiType} Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff + (7.5 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
                print(f"ATK (With 23 (Max) {kiType} Ki Spheres obtained):")
                calcATKCond(characterKit, copyCond, atkPerBuff + (23 * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("Starting from the ") and condition.__contains__(" turn from the "):
            turn = condition.split('Starting from the ')[1]
            print(f'ATK (Before the {turn}:')
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            
            print(f'ATK {condition}:')
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("turn(s) from the character's entry turn"):
            turn = (condition.split('For ')[1]).split(' turn(s)')[0]
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            print(f"ATK (After {turn} turn buff):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__(" per ") and condition.__contains__(" ally on the team")):
            category = condition.split(" per ")[1]
            category = category.split(" ally")[0]
            
            limitLoop = 8
            if "limit" in locals():
                limitLoop = int(limit/int(buff))+1
            for i in range(0, limitLoop):
                if i == 1:
                    print(f'ATK (With {str(i)} {category} ally on the team):')
                else:
                    print(f'ATK (With {str(i)} {category} allies on the team):')
                if flat:
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (i * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    calcATKCond(characterKit, copyCond, atkPerBuff + (i * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("Per ") and condition.__contains__(" ally on the team"):
            category = condition.split("er ")[1]
            category = category.split(" ally")[0]
            
            limitLoop = 8
            if "limit" in locals():
                limitLoop = int(limit/int(buff))+1
            for i in range(1, limitLoop):
                if i == 1:
                    print(f'ATK (With {str(i)} {category} ally on the team):')
                else:
                    print(f'ATK (With {str(i)} {category} allies on the team):')
                if flat:
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (i * int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    calcATKCond(characterKit, copyCond, atkPerBuff + (i * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__("Per ") and condition.__contains__(" Category ally attacking in the same turn")):
            category = condition.split("Per ")[1]
            category = category.split(" Category")[0]
            
            if condition.__contains__("self excluded"):
                for i in range(0, 3):
                    if i == 0:
                        print("ATK (With no other " + category + " Category allies attacking in the same turn):")
                    elif i == 1:
                        print("ATK (With another " + category + " Category ally attacking in the same turn):")
                    else:
                        print("ATK (With another " + str(i) + " " + category + " Category allies attacking in the same turn):")
                    if flat:
                        calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (i * buff), linkBuffs, onAttackATK, crit, superEffective, additional)
                    else:
                        calcATKCond(characterKit, copyCond, atkPerBuff + (i * buff), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            else:
                for i in range(1, 4):
                    if i == 0:
                        print("ATK (With no other " + category + " Category ally attacking in the same turn):")
                    elif i == 1:
                        print("ATK (With " + str(i) + " " + category + " Category ally attacking in the same turn):")
                    else:
                        print("ATK (With " + str(i) + " " + category + " Category allies attacking in the same turn):")
                    if flat:
                        calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (i * buff), linkBuffs, onAttackATK, crit, superEffective, additional)
                    else:
                        calcATKCond(characterKit, copyCond, atkPerBuff + (i * buff), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__("If the character's Ki is ")):
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)        
        elif (condition.__contains__("Per existing enemy")):
            limitLoop = 8
            if "limit" in locals():
                limitLoop = int(limit/buff)+1
            for i in range(1, limitLoop):
                if i == 1:
                    print(f'ATK (When facing {str(i)} enemy):')
                else:
                    print(f'ATK (When facing {str(i)} enemies):')
                    
                if flat:
                    calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff + (i*int(buff)), linkBuffs, onAttackATK, crit, superEffective, additional)
                else:
                    calcATKCond(characterKit, copyCond, atkPerBuff + (i*int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__("At the start of each turn")):
            for i in range(0, 7):
                print(f'ATK (Turn {str(i+1)}):')
                calcATKCond(characterKit, copyCond, atkPerBuff + (i * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__("at the start of each turn")):
            cond1 = condition.split(', at')[0]            
            cond1 = cond1.replace(' is on ', ' is not on ')
            print(f"ATK {cond1}):")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            
            cond1 = cond1.replace(' is not on ', ' is on ')
            limitLoop = 8
            if "limit" in locals():
                limitLoop = int(limit/int(buff))+1
            for i in range(1, limitLoop):
                print(f'ATK {cond1}, turn {str(i)}):')
                calcATKCond(characterKit, copyCond, atkPerBuff + (i * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif (condition.__contains__("For every turn passed from the start of battle")):
            limitLoop = 8
            if "limit" in locals():
                limitLoop = int(limit/int(buff))+1

            for i in range(0, limitLoop):
                print(f'ATK ({str(i)} turns passed):')
                calcATKCond(characterKit, copyCond, atkPerBuff + (i * int(buff)), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        elif condition.__contains__("The more HP remaining"):
            for i in range(101):
                if i % 10 == 0:
                    print("ATK at " + str(i) + "% HP:")
                    if flat:
                        calcATKCond(characterKit, copyCond, atkPerBuff, int(atkFlatBuff + (buff*(i/100))), linkBuffs, onAttackATK, crit, superEffective, additional)
                    else:
                        calcATKCond(characterKit, copyCond, int(atkPerBuff + (buff*(i/100))), atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
        else:
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, newPerBuff, newFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
            
            condition = condition.replace(' is ', ' is not ')
            condition = condition.replace('As ', 'Not as ')
            condition = condition.replace('When facing ', 'When not facing ')
            condition = condition.replace(' are ', ' are not ')
            condition = condition.replace(' obtained', ' not obtained')
            
            print(f"ATK {condition}:")
            calcATKCond(characterKit, copyCond, atkPerBuff, atkFlatBuff, linkBuffs, onAttackATK, crit, superEffective, additional)
    else:
        print(f'{characterKit.stats[1]} (Base ATK Stat)')
        # Duo 200% lead by default
        lead = 5
        # Dev note: Temp condition, checks for units supported under 220% leads:
        # - Vegto, Gogta, SSBE, Monke, Rice, Frank, Ultra Vegeta 1, Fishku
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
        "Universe Survival Saga" in characterKit.categories or 
        "Giant Ape Power" in characterKit.categories or
        "Full Power" in characterKit.categories or 
        "Battle of Fate" in characterKit.categories):
            lead = 5.4
        ATK = int(characterKit.stats[1]*lead) # Apply leader skill
        print(f'{ATK} (With Duo {int(((lead-1)*100)/2)}% Leader Skill)')
        ATK = int(ATK * (1 + (atkPerBuff/100))) # Apply SoT percentage buffs
        print(f'{ATK} (With {atkPerBuff}% Passive Buff)')
        ATK = int(ATK + atkFlatBuff) # Apply SoT flat buffs
        print(f'{ATK} (With {atkFlatBuff} Flat Passive Buff)')
        ATK = int(ATK + (ATK * (linkBuffs/100))) # Apply link buffs
        print(f'{ATK} (With {linkBuffs}% Link Skill Buff)')
        
        for SAName, SAEffect, kiValue in zip(characterKit.SANames, characterKit.SAEffects, characterKit.kiValues):
            newKiMultiplier = (int(characterKit.kiMultiplier)/24)*(12+int(kiValue))
            ATKnew = int(ATK * (newKiMultiplier/100)) # Apply Ki multiplier
            print(f'{ATKnew} (With {newKiMultiplier}% Ki Multiplier)')
            print(f"Launching Super Attack: {SAName} at {kiValue} Ki")
            calcATKSA(kiValue, SAName, SAEffect, ATKnew, onAttackATK, 0, 0, "", crit, superEffective, additional)
        if int(kiValue) < 12:
            ATKnew = int(ATK * (int(characterKit.kiMultiplier)/100)) # Apply Ki multiplier
            print(f'{ATKnew} (With {characterKit.kiMultiplier}% Ki Multiplier)')
            print(f"Launching Super Attack: {SAName} at 12 Ki")
            calcATKSA(12, SAName, SAEffect, ATKnew, onAttackATK, 0, 0, "", crit, superEffective, additional)
        if characterKit.rank == "LR" and int(kiValue) < 18:
            print(f'{ATKnew} (With {(((200-characterKit.kiMultiplier)/2)+characterKit.kiMultiplier)}% Ki Multiplier)')
            print(f"Launching Super Attack: {SAName} at 18 Ki")
            ATKnew = int(ATK * ((((200-characterKit.kiMultiplier)/2)+characterKit.kiMultiplier)/100)) # Apply Ki multiplier
            calcATKSA(18, SAName, SAEffect, ATKnew, onAttackATK, 0, 0, "", crit, superEffective, additional)
        if characterKit.rank == "LR":
            print(f'{ATKnew} (With 200% Ki Multiplier)')
            print(f"Launching Super Attack: {SAName} at 24 Ki")
            ATKnew = int(ATK * 2) # Apply Ki multiplier
            calcATKSA(24, SAName, SAEffect, ATKnew, onAttackATK, 0, 0, "", crit, superEffective, additional)
    
# Read through kit, sepearate lines based on activiation condition (SoT vs. 'on attack')
# Then, calculate SoT attack and conditional SoT attack  
def calculateMain(characterKit, atkLinkBuffs, defLinkBuffs, crit):   
    condSoTATK = LinkedList()
    condSoTDEF = LinkedList()
    onAttackATK = LinkedList()
    onAttackDEF = LinkedList()

    buff = 0
    atkPerBuff = 0
    defPerBuff = 0
    atkFlatBuff = 0
    defFlatBuff = 0
    condition = ""
    flat = False
    additional = 0
    superEffective = False
    for line in (characterKit.passive).splitlines():
        if (((line.__contains__("Enemies'") or line.__contains__("enemies'") or
        line.__contains__("Enemy's") or line.__contains__("enemy's")) and
        not line.__contains__('allies')) or
        (line.__contains__('Type allies') and not line.__contains__(characterKit.type)) or
        (line.__contains__('Class allies') and not line.__contains__(characterKit.unitClass)) or
        (line.__contains__("(self excluded)") and not line.__contains__('*'))):
            continue

        if line.__contains__("*"):
            condition = line[1:line.find(":")]
        
        if line.__contains__("allies' ") and line.__contains__('and if there is '):
            ally = line.split("allies' ")[0]
            cond1 = ('if there is ' + line.split(" and if there is ")[1])
            cond2 = cond1.split(", ")[1]
            cond2 = cond2.replace('plus an additional', ally + "allies'")
            cond1 = "*" + cond1[0:1].capitalize() + (cond1[1:].split(", ")[0])
            characterKit.passive += f'\n\n{cond1}:\n{cond2}'
            
            line = line.split(" and if there is ")[0]
        elif line.__contains__("allies' ") and line.__contains__(', plus an additional '):
            ally = line.split("allies' ")[0]
            cond = line.split(', plus an additional')[1:]
            line = line.split(", plus an additional ")[0]
            
            for part in cond:
                print(part)
                if part.__contains__('for characters who also belong to the '):
                    buff2 = part.split('ATK & DEF ')[1]
                    buff2 = int(buff2.split('%{')[0])
                    ally2 = part.split("for characters who also belong to the '")[1]
                    ally2 = ally2.split("' Category")[0]
                    
                    if ally2 in characterKit.categories:
                        if flat:
                            atkFlatBuff += buff2
                            defFlatBuff += buff2
                        else:
                            atkPerBuff += buff2
                            defPerBuff += buff2
                else:
                    print(cond)
                    part = ally + "allies'" + part
                    print(part)
                    cond1 = '(When' + part.split(' when')[1] + ')'
                    cond2 = (part.split(' when')[0]).replace('{passiveImg:up_g}', '')
                    
                    cond3 = f'{cond2} {cond1}'
                    if cond2.__contains__('ATK'):
                        cond4 = cond3.replace('ATK ', "ATK +")
                        cond4 = cond4.replace('& DEF ', "")
                        condSoTATK.insertLine(cond4)
                    if cond2.__contains__('DEF'):
                        cond4 = cond3.replace('DEF ', "DEF +")
                        cond4 = cond4.replace('ATK & ', "")
                        condSoTDEF.insertLine(cond4)
            
        if (line.__contains__("hance of performing a critical hit") or
        line.__contains__("Performs a critical hit")):
            crit = True
            additional += 1
            
        if line.__contains__('and chance of performing a critical hit'):
            line1 = line.split('and chance of performing a critical hit ')[0]
            line2 = line.split(' and chance of performing a critical hit ')[1]
            line2 = line2.split('} ')[1]
            line = line1 + line2
        line = line.replace('and performs a critical hit ', '')
        
        if line.__contains__("Attacks are effective against all Types"):
            superEffective = True
            additional += 1
            
        if (((line.__contains__("Launches an additional attack that has a") or
        line.__contains__("chance of launching an additional attack that has a")) and
        line.__contains__("chance of becoming a Super Attack")) or 
        line.__contains__("Launches an additional Super Attack") or 
        line.__contains__("launching an additional Super Attack")):
            additional += 1
            
        if ((line.__contains__("Counters with ") or
             line.__contains__("counters with ") or
             line.__contains__("countering with ")) and
            line.__contains__(" power")):
            onAttackATK.insertLine(line + " (" + condition + ")")
        
        if line.__contains__('ATK '):
            atkBuff = line[line.find('ATK ')+4:]
            
            secondEffect = ''
            if line.__contains__('hance of ') and not line.__contains__('hance of performing a critical hit'):
                secondEffect = ', ' + line.split('hance of')[0] + 'hance'
                secondEffect = (secondEffect.replace('- ', '')).capitalize()
            elif line.__contains__('{passiveImg:once}'):
                secondEffect = ', once only'
                
            if atkBuff.__contains__('} ('):
                secondEffect = secondEffect + ' ' + atkBuff.split('} ')[1]
            elif atkBuff.__contains__('} and DEF '):
                secondEffect = atkBuff[atkBuff.find('} ')+1:]
                secondEffect = ', ' + secondEffect[secondEffect.find('} ')+2:]
            elif atkBuff.__contains__('} '):
                secondEffect = secondEffect + ', ' + atkBuff.split('} ')[1]
                
            if atkBuff.__contains__('} and DEF '):
                atkBuff = atkBuff.split(' and DEF ')[0]
            elif atkBuff.__contains__('DEF '):
                atkBuff = atkBuff.split('DEF ')[1]
            
            if atkBuff.__contains__('{passiveImg:up_g}'):
                atkBuff = '+' + atkBuff[:atkBuff.find('{passiveImg')]
            elif atkBuff.__contains__('{passiveImg:down_r}'):
                atkBuff = '-' + atkBuff[:atkBuff.find('{passiveImg')]
                
            if atkBuff.__contains__('%'):
                flat = False
            else:
                flat = True
            
            # Dev Note: For condition/on attack passives with multiple ATK buffs, combine
            # ATK buffs as to not cause confusion in readibility (i.e. PHY King Cold, AGL 10 Year Goku)
            if condition.__contains__('Basic effect'):
                if (line.__contains__("hance of ") and line.__contains__(" ATK ")):
                    RNG = line.split("hance of")[0]
                    RNG = RNG.split("- ")[1]
                    condSoTATK.insertLine(f'ATK {atkBuff} ({RNG}hance)')
                elif (line.__contains__("- {passiveImg:once}")):
                    condSoTATK.insertLine(f'ATK {atkBuff} (Once only)')
                else:
                    if not flat:
                        atkBuff = atkBuff.split('%')[0]
                
                    if '+' in atkBuff:
                        atkBuff = int(atkBuff.split('+')[1])
                    else:
                        atkBuff = -1*int(atkBuff.split('-')[1])
                    
                    if flat:
                        atkFlatBuff += atkBuff
                    else:
                        atkPerBuff += atkBuff
            elif (condition.__contains__("When attacking") or
            condition.__contains__("when attacking") or secondEffect.__contains__("when attacking") or
            condition.__contains__("final blow") or
            condition.__contains__("receiving an attack") or
            condition.__contains__("After guard is activated") or
            condition.__contains__("For every attack evaded") or
            condition.__contains__("For every attack performed") or
            condition.__contains__("For every Super Attack performed") or
            condition.__contains__("For every attack received") or
            (condition.__contains__("After performing ") and condition.__contains__("ttack(s) in battle")) or
            (condition.__contains__("After receiving ") and condition.__contains__("ttacks in battle")) or
            condition.__contains__("After performing a Super Attack") or
            condition.__contains__("When the target enemy is in the following status: ")):
                atkLine = f"ATK {atkBuff} ({condition}{secondEffect})"                
                onAttackATK.insertLine(atkLine)
            else:
                atkLine = f"ATK {atkBuff} ({condition}{secondEffect})"
                condSoTATK.insertLine(atkLine)
            
        if line.__contains__('DEF'):
            defBuff = line[line.find('DEF ')+4:]
            
            secondEffect = ''
            if line.__contains__('hance of '):
                secondEffect = ', ' + line.split('hance of')[0] + 'hance'
                secondEffect = (secondEffect.replace('- ', '')).capitalize()
            if defBuff.__contains__('} ('):
                secondEffect = secondEffect + ' ' + defBuff.split('} ')[1]
            elif defBuff.__contains__('} '):
                secondEffect = secondEffect + ', ' + defBuff.split('} ')[1]
            
            if defBuff.__contains__('{passiveImg:up_g}'):
                defBuff = '+' + defBuff[:defBuff.find('{passiveImg')]
            elif defBuff.__contains__('{passiveImg:down_r}'):
                defBuff = '-' + defBuff[:defBuff.find('{passiveImg')]
                
            if defBuff.__contains__('%'):
                flat = False
            else:
                flat = True
            
            if condition.__contains__('Basic effect'):
                if (line.__contains__("hance of ") and line.__contains__(" DEF")):
                    RNG = line.split("hance of")[0]
                    RNG = RNG.split("- ")[1]
                    condSoTDEF.insertLine(f'DEF {atkBuff} ({RNG}hance)')
                else:
                    if not flat:
                        defBuff = defBuff.split('%')[0]
                
                    if '+' in defBuff:
                        defBuff = int(defBuff.split('+')[1])
                    else:
                        defBuff = -1*int(defBuff.split('-')[1])
                    
                    if flat:
                        defFlatBuff += defBuff
                    else:
                        defPerBuff += defBuff
            elif (condition.__contains__("When attacking") or
            condition.__contains__("when attacking") or
            condition.__contains__("final blow") or
            condition.__contains__("receiving an attack") or
            condition.__contains__("After guard is activated") or
            condition.__contains__("For every attack evaded") or
            condition.__contains__("For every attack performed") or
            condition.__contains__("For every Super Attack performed") or
            condition.__contains__("For every attack received") or
            (condition.__contains__("After performing ") and condition.__contains__("ttack(s) in battle")) or
            (condition.__contains__("After receiving ") and condition.__contains__("ttacks in battle")) or
            condition.__contains__("After performing a Super Attack") or
            condition.__contains__("When the target enemy is in the following status: ")):
                defLine = f"ATK {defBuff} ({condition}{secondEffect})"                
                onAttackDEF.insertLine(defLine)
            else:
                defLine = f"ATK {defBuff} ({condition}{secondEffect})"                
                condSoTDEF.insertLine(defLine)
    print(f"\nInitial percent buffs: {atkPerBuff}% ATK, {defPerBuff}% DEF")
    print(f"Initial flat buffs: {atkFlatBuff} ATK, {defFlatBuff} DEF\n")
    calcATKCond(characterKit, condSoTATK, atkPerBuff, atkFlatBuff, atkLinkBuffs, onAttackATK, crit, superEffective, additional)
    #calcDEFCond(characterKit, condSoTDEF, defLinkBuffs, onAttackDEF, crit, superEffective, additional, 1)
    
# Read through kit, sepearate lines based on activiation condition (SoT vs. 'on attack')
# Then, calculate SoT defense and conditional SoT defense  
def calculateStats(characterKit, partnerKit):
    os.system('cls')
    print(f"Calculating: {characterKit.rank} {characterKit.type} {characterKit.name} (Linked with {partnerKit.rank} {partnerKit.type} {partnerKit.name}):")
    
    # Find all shared links
    sharedLinks = []
    i = 0
    if (characterKit.name != partnerKit.name or int(partnerKit.id) >= 4000000):
        print("\nShared Links:")
        for sharedLink in characterKit.links:
            if sharedLink in partnerKit.links:
                print(f"- {sharedLink} - {characterKit.linkBuffs[i]}")
                sharedLinks.append(characterKit.linkBuffs[i])
            i = i + 1
    else:
        print("Unit cannot link with partner (Shared name)")
        calculateMain(characterKit, 0, 0, False)
        return

    if not sharedLinks:
        print("Unit cannot link with partner (No shared links)")
        calculateMain(characterKit, 0, 0, False)
        return
    else:
        # Calculate shared link buffs
        kiLinkBuffs = 0
        atkLinkBuffs = 0
        defLinkBuffs = 0
        critLinkBuffs = 0
        evadeLinkBuffs = 0
        damageReduceLinkBuffs = 0
        recoveryLinkBuffs = 0
        atkLinkDebuffs = 0
        defLinkDebuffs = 0
        crit = False
    
        for linkStats in sharedLinks:
            if linkStats.__contains__("Ki +"):
                kiBuff = linkStats[linkStats.find('Ki +')+4:]
                if kiBuff.__contains__(' '):
                    kiBuff = kiBuff[:kiBuff.find(' ')]
                if kiBuff.__contains__(';'):
                    kiBuff = kiBuff[:kiBuff.find(';')]
                if kiBuff.__contains__(','):
                    kiBuff = kiBuff[:kiBuff.find(',')]
                kiLinkBuffs += int(kiBuff)
            if (linkStats.__contains__("ATK +") or
            linkStats.__contains__("ATK & ") or
            linkStats.__contains__("ATK, DEF &")):
                atkBuff = linkStats[linkStats.find('ATK ')+4:]
                if linkStats.__contains__("plus an additional ATK +"):
                    atkBuff2 = atkBuff[atkBuff.find('ATK +')+5:]
                    atkBuff2 = atkBuff2[:atkBuff2.find('%')]
                    atkLinkBuffs += int(atkBuff2)
                atkBuff = atkBuff[atkBuff.find('+')+1:]
                atkBuff = atkBuff[:atkBuff.find('%')]
                atkLinkBuffs += int(atkBuff)
            if linkStats.__contains__("DEF +"):
                defBuff = linkStats[linkStats.find('DEF +')+5:]
                defBuff = defBuff[:defBuff.find('%')]
                defLinkBuffs += int(defBuff)
            if linkStats.__contains__("chance of performing a critical hit +"):
                crit = True
                critBuff = linkStats[linkStats.find('chance of performing a critical hit +')+37:]
                critBuff = critBuff[:critBuff.find('%')]
                critLinkBuffs += int(critBuff)
            if linkStats.__contains__("chance of evading enemy's attack"):
                evadeBuff = linkStats[linkStats.find('chance of evading enemy')+59:]
                evadeBuff = evadeBuff[:evadeBuff.find('%')]
                evadeLinkBuffs += int(evadeBuff)
            if linkStats.__contains__("reduces damage received by "):
                damageReduceBuff = linkStats[linkStats.find('reduces damage received by ')+27:]
                damageReduceBuff = damageReduceBuff[:damageReduceBuff.find('%')]
                damageReduceLinkBuffs += int(damageReduceBuff)
            if linkStats.__contains__("ecovers "):
                recoveryBuff = linkStats[linkStats.find('ecovers ')+8:]
                recoveryBuff = recoveryBuff[:recoveryBuff.find('% HP')]
                recoveryLinkBuffs += int(recoveryBuff)
            if linkStats.__contains__("enemies' DEF -"):
                defDebuff = linkStats[linkStats.find('DEF -')+5:]
                defDebuff = defDebuff[:defDebuff.find('%')]
                defLinkDebuffs += int(defDebuff)
        print(f"\nTotal Link Buffs:")
        print(f"- Ki +{str(kiLinkBuffs)}, ATK +{str(atkLinkBuffs)}%, DEF +{str(defLinkBuffs)}%")
        print(f"- Chance of performing a critical hit +{str(critLinkBuffs)}%")
        print(f"- Chance of evading enemy's attack +{evadeLinkBuffs}%")
        print(f"- Damage reduction rate +{damageReduceLinkBuffs}%")
        print(f"- Recovers {recoveryLinkBuffs}% HP")
        print(f"- All enemies' DEF -{defLinkDebuffs}%")
        
        calculateMain(characterKit, atkLinkBuffs, defLinkBuffs, crit)
   
# Helper method to get all unit details
def getPartnerKit(partnerID):      
    partnerKit = []
    
    unitURL = f'https://dokkan.fyi/characters/{partnerID}'
    
    # Send a GET request to fetch the webpage content (Returns None if page fails)
    if (requests.get(unitURL)).status_code == 200:       
        response = (requests.get(unitURL)).text
    
        titleInfo = response[response.find('Details & link partners for DRAGON BALL Z Dokkan Battle character ')+66:response.find('. |')]
        
        # Search for EZA
        if response.__contains__('Super Extreme Z-Awakened '):
            titleInfo = titleInfo[titleInfo.find('Super Extreme Z-Awakened ')+25:]
        elif response.__contains__('Extreme Z-Awakened '):
            titleInfo = titleInfo[titleInfo.find('Extreme Z-Awakened ')+19:]
            
        os.system('cls')
        print('Retrieving unit information...')
        
        rank = titleInfo.split()[0]
        
        # Dev Note: No class information (Super/Extreme) listed for N/R/SR units
        # Using Hydros' site as temporary solution if N/R/SR unit is found
        if rank == 'UR' or rank == 'LR':
            type = titleInfo.split()[2]
        else:
            tempResponse = (requests.get(f'https://dokkanbattle.net/card/{partnerID}')).text
            type = titleInfo.split()[1]
        # Fix name (Not sure on case, units with mulitple words in name? (Nappa a (Giant Ape)))
        name = titleInfo[titleInfo.find(type)+4:]
        
        if partnerID >= 4000000:
            name += (' (<->)')
        
        if (partnerID == '1010640' or partnerID == '1010650' or 
        partnerID == '1010630' or partnerID == '1011041'):
            type = 'STR/INT'
                
        links = retrieveLinks(response)[0]
        
        # Create object containing all unit kit details
        characterKit = Partner(partnerID, type, rank, name, links)

        os.system('cls')
        return characterKit
    else:
        print('Failed to retrieve character information.')
        return None
    
# Helper method to get all unit details
def getKit(characterID):
    characterKit = []
    
    originID = characterID
    if characterID % 2 == 0:
        characterID += 1
    
    unitURL = f'https://dokkan.fyi/characters/{originID}'
    
    # Send a GET request to fetch the webpage content (Returns None if page fails)
    if (requests.get(unitURL)).status_code == 200:       
        response = (requests.get(unitURL)).text
    
        titleInfo = response[response.find('Details & link partners for DRAGON BALL Z Dokkan Battle character ')+66:response.find('. |')]
        
        # Search for EZA
        EZA = 0
        if response.__contains__('Super Extreme Z-Awakened '):
            # SEZA selection
            EZA = input('Select option for EZA (0 - Base; 1 - EZA; 2 - SEZA): ')
            titleInfo = titleInfo[titleInfo.find('Super Extreme Z-Awakened ')+25:]
        elif response.__contains__('Extreme Z-Awakened '):
            # EZA selection
            EZA = input('Select option for EZA (0 - Base; 1 - EZA): ')
            titleInfo = titleInfo[titleInfo.find('Extreme Z-Awakened ')+19:]
            
        os.system('cls')
        print('Retrieving unit information...')
        
        rank = titleInfo.split()[0]
        
        # Dev Note: No class information (Super/Extreme) listed for N/R/SR units
        # Using Hydros' site as temporary solution if N/R/SR unit is found
        if rank == 'UR' or rank == 'LR':
            unitClass = titleInfo.split()[1]
            type = titleInfo.split()[2]
        elif rank == 'SSR':
            tempInfo = (requests.get(f'https://dokkan.fyi/characters/{characterID}')).text
            tempInfo = tempInfo[tempInfo.find('Details & link partners for DRAGON BALL Z Dokkan Battle character ')+66:tempInfo.find('. |')]
            unitClass = tempInfo.split()[1]
            type = tempInfo.split()[2]
        else:
            tempResponse = (requests.get(f'https://dokkanbattle.net/card/{characterID}')).text
            if tempResponse.__contains__('element EXTREME'):
                unitClass = 'Extreme'
            else:
                unitClass = 'Super'
            type = titleInfo.split()[1]
        # Fix name (Not sure on case, units with mulitple words in name? (Nappa a (Giant Ape)))
        name = titleInfo[titleInfo.find(type)+4:]
        
        if (originID == 1010640 or originID == 1010650 or 
        originID == 1010630 or originID == 1011041):
            type = 'STR/INT'
        
        transform = ''
        # Set ID of transformed card if detected
        if response.__contains__('shadow-inner !border-b-0 !text-sm lowercase hover:cursor-pointer'):
            transform = response[response.find('shadow-inner !border-b-0 !text-sm lowercase hover:cursor-pointer')+102:]
            transform = transform[:transform.find('"><div class="px-1 drop-shadow')]
                
        title = response[response.find('<title inertia>')+15:response.find(name)-1]
        lead = retrieveLead(response, rank, EZA)
        SANames, SAEffects, kiValues, kiMultiplier = retrieveSA(response, rank, EZA)
        passiveName, passive = retrievePassive(response, rank, EZA)
        links, linkBuffs = retrieveLinks(response)
        categories = retrieveCategories(response)
        
        response = (requests.get(f'https://dokkan.fyi/characters/{characterID}')).text
        stats = retrieveStats(response, characterID, EZA, rank)
        
        if characterID >= 4000000:
            name += (' (<->)')
        
        # Create object containing all unit kit details
        characterKit = Unit(characterID, unitClass, type, rank, title, 
        name, lead, SANames, SAEffects, passiveName, passive, links, linkBuffs,
        categories, stats, kiValues, kiMultiplier, transform)

        os.system('cls')
        return characterKit
    else:
        print('Failed to retrieve character information.')
        return None

def main(characterID):
    mainUnit = getKit(characterID)
    print(f'{mainUnit.unitClass} {mainUnit.type} {mainUnit.rank} {mainUnit.title} {mainUnit.name}')
    print(f'\nLeader Skill: {mainUnit.lead}')
    
    for SAName, SAEffect in zip(mainUnit.SANames, mainUnit.SAEffects):
        print(f'\nSuper Attack: {SAName} - {SAEffect}')
    
    print(f'\nPassive Skill: {mainUnit.passiveName}')
    print(mainUnit.passive)
    print('\nLink Skills:')
    print(mainUnit.links)
    print(f'\nCategories:\n{mainUnit.categories}')
    
    if (mainUnit.rank == 'SSR' or mainUnit.rank == 'UR' or mainUnit.rank == 'LR'):
        print('\nMax Stats (100%): ')
    else:
        print('\nMax Stats: ')
        
    print(f'HP: {mainUnit.stats[0]} | ATK: {mainUnit.stats[1]} | DEF: {mainUnit.stats[2]}')
    
    if not mainUnit.links:
        calculateStats(mainUnit, mainUnit)
    else:
        partnerID = int(input("Enter the partner character's Card ID from Dokkan.FYI: "))
        partnerKit = getPartnerKit(partnerID)
        calculateStats(mainUnit, partnerKit)
    
    if mainUnit.transform != '':
        input("Click any button to continue with transformed form:")
        main(int(mainUnit.transform))
    else:
        input("Click any button to finish the program:")
    
os.system('cls') # Clears terminal; replace with os.system('clear') if on Unix/Linux/Mac
print("Welcome to Manila's Dokkan Calculator (Powered by Dokkan.FYI by CapnMZ)")
characterID = int(input("Enter the tested character's Card ID from Dokkan.FYI: "))
main(characterID)