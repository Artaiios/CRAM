#!/usr/bin/env python3
"""
Build CRAM demo configs (DE + EN variant) for v2.2.

Output:
  repo/demo/cram-demo-enterprise-de.json
  repo/demo/cram-demo-enterprise-en.json

Structure:
  4 Levels: Strategisch / Taktisch / Fachbereich / Operativ
  ~28 roles total
  ~70 unique persons (Latin-script only, international mix)
  5 skill-based pools attached to operative-level lead roles
  1 absent person as anchor to demonstrate cascade
"""

import json
import datetime as dt
from pathlib import Path

# ---------------------------------------------------------------------------
# Person pool — international names, Latin script only
# (Asian names romanised: e.g. "Wang Lei" not "王磊"; "Tanaka Akira" not "田中明")
# Each person carries id, name, phone, email, keywords (V2.1+ field).
# ---------------------------------------------------------------------------

PERSONS = [
    # --- DE / AT / CH (10) ---
    ("Dr. Mirja Bachmeier",       "+49 172 1000001", "mirja.bachmeier@example.com",       ["Krisenmanagement", "Vorstand"]),
    ("Sebastian Köhler",          "+49 170 1000002", "sebastian.koehler@example.com",     ["Krisenmanagement", "Recht"]),
    ("Dr. Franziska Öztürk",      "+49 173 1000003", "franziska.oeztuerk@example.com",    ["Kommunikation", "Public Affairs"]),
    ("Matthias Großmann",         "+49 170 1000004", "matthias.grossmann@example.com",    ["Recht", "Compliance"]),
    ("Elena Süßmann",             "+43 660 1000005", "elena.suessmann@example.com",       ["Risk", "Audit"]),
    ("Lukas Brunner",             "+41 79 1000006",  "lukas.brunner@example.com",         ["Finance", "Treasury"]),
    ("Hannah Vogel",              "+49 151 1000071", "hannah.vogel@example.com",          ["HR", "Crisis Response"]),
    ("Klaus Engelhardt",          "+49 162 1000072", "klaus.engelhardt@example.com",      ["Facilities", "Security"]),
    ("Marlene Roth",              "+49 175 1000073", "marlene.roth@example.com",          ["Datenschutz", "DSGVO"]),
    ("Tobias Steinmann",          "+41 76 1000074",  "tobias.steinmann@example.com",      ["IT-Operations", "Cloud"]),

    # --- FR / BE / LU (8) ---
    ("Margaux Lefèvre",           "+33 6 10 00 00 07","margaux.lefevre@example.com",      ["Krisenmanagement", "BCM"]),
    ("Thibault Mercier",          "+33 6 10 00 00 08","thibault.mercier@example.com",     ["Physical Security", "Incident Command"]),
    ("Amélie Rousseau",           "+33 6 10 00 00 09","amelie.rousseau@example.com",      ["Business Continuity", "Recovery"]),
    ("Joost van der Berg",        "+31 6 10 00 00 10","joost.vandenberg@example.com",     ["Krisenmanagement", "Operations"]),
    ("Camille Dubois",            "+33 6 10 00 00 11","camille.dubois@example.com",       ["Forensics", "Malware"]),
    ("Pierre Lambert",            "+32 470 1000012", "pierre.lambert@example.com",        ["Network Security", "DDoS"]),
    ("Sophie Vermeulen",          "+32 478 1000013", "sophie.vermeulen@example.com",      ["Application Security", "AppSec"]),
    ("Henri Bouchard",            "+33 6 10 00 00 14","henri.bouchard@example.com",       ["Legal", "Privacy"]),

    # --- IT / ES / PT (8) ---
    ("Francesca Lombardi",        "+39 340 1000011", "francesca.lombardi@example.com",    ["Kommunikation", "Media"]),
    ("Giovanni Moretti",          "+39 340 1000012", "giovanni.moretti@example.com",      ["Recht", "Compliance"]),
    ("Beatriz Mendoza",           "+34 612 1000040", "beatriz.mendoza@example.com",       ["Forensics", "Memory Analysis"]),
    ("Joana Carvalho",            "+351 912 100015", "joana.carvalho@example.com",        ["CISO", "Governance"]),
    ("Mateo García",              "+34 612 1000016", "mateo.garcia@example.com",          ["Identity", "IAM"]),
    ("Inés Romero",               "+34 612 1000017", "ines.romero@example.com",           ["SOC", "Threat Hunting"]),
    ("Rafael Gonçalves",          "+351 912 100018", "rafael.goncalves@example.com",      ["Incident Response", "Containment"]),
    ("Lucia Esposito",            "+39 340 1000019", "lucia.esposito@example.com",        ["Comms", "Internal"]),

    # --- UK / IE / Nordics (8) ---
    ("Sarah O'Connor",            "+1 617 555 0025", "sarah.oconnor@example.com",         ["External Relations", "Press"]),
    ("Declan O'Sullivan",         "+353 85 1000022", "declan.osullivan@example.com",      ["DPO", "Privacy"]),
    ("Eleanor Whitfield",         "+44 7700 100021", "eleanor.whitfield@example.com",     ["Finance", "Treasury"]),
    ("Astrid Lindqvist",          "+46 70 1000016",  "astrid.lindqvist@example.com",      ["IT-Operations", "Linux"]),
    ("Aino Virtanen",             "+358 40 1000018", "aino.virtanen@example.com",         ["Application Development", "DevSecOps"]),
    ("Connor MacDonald",          "+44 7700 100030", "connor.macdonald@example.com",      ["SOC", "EMEA"]),
    ("Niall Byrne",               "+353 85 1000031", "niall.byrne@example.com",           ["Forensics", "Disk Analysis"]),
    ("Erik Holmberg",             "+46 70 1000032",  "erik.holmberg@example.com",         ["Recovery", "Backup"]),

    # --- North America (8) ---
    ("Jennifer Martinez-Klein",   "+1 415 555 0023", "jennifer.martinezklein@example.com",["Physical Security", "Americas"]),
    ("Priya Patel-Johnson",       "+1 206 555 0027", "priya.pateljohnson@example.com",    ["SOC", "Shift Lead"]),
    ("Benjamin Goldstein",        "+1 202 555 0028", "benjamin.goldstein@example.com",    ["Network Operations", "Firewall"]),
    ("Marcus Thompson",           "+1 212 555 0024", "marcus.thompson@example.com",       ["Communications", "Customer Care"]),
    ("Olivia Carter",             "+1 415 555 0033", "olivia.carter@example.com",         ["AppSec", "SAST"]),
    ("Daniel Rivera",             "+1 312 555 0034", "daniel.rivera@example.com",         ["SOC", "Threat Intel"]),
    ("Hannah Bennett",            "+1 617 555 0035", "hannah.bennett@example.com",        ["Incident Response", "Triage"]),
    ("Ethan Walker",              "+1 312 555 0036", "ethan.walker@example.com",          ["IT-Recovery", "Restore"]),

    # --- LATAM (6) ---
    ("Matías Fernández",          "+54 11 1000037",  "matias.fernandez@example.com",      ["Endpoint", "Argentina"]),
    ("Isabella Herrera",          "+57 300 1000038", "isabella.herrera@example.com",      ["Supply Chain", "Recovery"]),
    ("Joaquín Ramírez",           "+52 55 1000039",  "joaquin.ramirez@example.com",       ["Forensics", "LATAM"]),
    ("Camila Vega",               "+56 9 1000041",   "camila.vega@example.com",           ["SOC", "Threat Hunting"]),
    ("Bruno Cardoso",             "+55 21 1000042",  "bruno.cardoso@example.com",         ["Network Security", "DDoS"]),
    ("Valentina Cruz",            "+57 300 1000043", "valentina.cruz@example.com",        ["Comms", "Spanish"]),

    # --- MENA / Africa (6) ---
    ("Youssef El Amrani",         "+212 6 1000048",  "youssef.elamrani@example.com",      ["Vulnerability Management", "Patching"]),
    ("Thandiwe Nkosi",            "+27 82 1000049",  "thandiwe.nkosi@example.com",        ["Identity", "Africa"]),
    ("Amina Hassan",              "+254 722 100045", "amina.hassan@example.com",          ["Facilities", "Physical"]),
    ("Kwame Mensah",              "+233 24 1000046", "kwame.mensah@example.com",          ["Recovery", "Backup"]),
    ("Layla Mansour",             "+971 50 1000047", "layla.mansour@example.com",         ["Legal", "Middle East"]),
    ("Omar Haddad",               "+962 79 1000050", "omar.haddad@example.com",           ["SOC", "Tier-2"]),

    # --- Asia-Pacific, Latin-romanised (10) ---
    ("Wang Lei",                  "+86 138 0000051", "wang.lei@example.com",              ["Cloud Security", "China"]),
    ("Tanaka Akira",              "+81 90 1000052",  "tanaka.akira@example.com",          ["Forensics", "Japan"]),
    ("Liu Yang",                  "+86 138 0000055", "liu.yang@example.com",              ["SOC", "APAC"]),
    ("Park Min-jun",              "+82 10 1000071",  "park.minjun@example.com",           ["Crisis Documentation", "Korea"]),
    ("Huang Xiulan",              "+86 138 0000056", "huang.xiulan@example.com",          ["Customer Care", "APAC"]),
    ("Chen Jing",                 "+86 138 0000054", "chen.jing@example.com",             ["Malware Analyst", "Reverse Engineering"]),
    ("Xu Mei",                    "+86 138 0000058", "xu.mei@example.com",                ["OT Security", "ICS"]),
    ("Meera Nair",                "+91 98 100 00064","meera.nair@example.com",            ["Cryptography", "Key Management"]),
    ("Siddharth Mehta",           "+91 98 100 00065","siddharth.mehta@example.com",       ["AppSec", "SDLC"]),
    ("Sato Yui",                  "+81 90 1000067",  "sato.yui@example.com",              ["Comms", "Japan"]),

    # --- Oceania (3) ---
    ("Mia Robertson",             "+61 4 1000061",   "mia.robertson@example.com",         ["IT-Operations", "Australia"]),
    ("Liam O'Brien",              "+61 4 1000062",   "liam.obrien@example.com",           ["SOC", "Pacific"]),
    ("Zoe Whitmore",              "+64 21 1000063",  "zoe.whitmore@example.com",          ["Recovery", "NZ"]),

    # --- Reserves / pool depth (3) ---
    ("Karim Boutros",             "+20 10 1000068",  "karim.boutros@example.com",         ["IR", "Tier-2"]),
    ("Nadia Reyes",               "+34 612 1000069", "nadia.reyes@example.com",           ["Legal", "Privacy"]),
    ("Felix Albrecht",            "+49 174 1000070", "felix.albrecht@example.com",        ["Recovery", "DR-Lead"]),
]

# Build persons array with stable IDs p1..pN
def build_persons():
    persons = []
    for i, (name, phone, email, keywords) in enumerate(PERSONS, start=1):
        persons.append({
            "id": f"p{i}",
            "name": name,
            "phone": phone,
            "email": email,
            "keywords": keywords,
        })
    return persons


# Helper for assignments by (1-indexed) person numbers
def A(*nums):
    return [{"personId": f"p{n}", "rank": rank} for rank, n in enumerate(nums)]


# ---------------------------------------------------------------------------
# 4-Level structure
# ---------------------------------------------------------------------------

#  Person mapping (1-indexed) — keep this in sync with PERSONS!
#  1..10  DE/AT/CH:   1=Bachmeier, 2=Köhler, 3=Öztürk, 4=Großmann, 5=Süßmann,
#                     6=Brunner, 7=Vogel, 8=Engelhardt, 9=Roth, 10=Steinmann
#  11..18 FR/BE/LU:   11=Lefèvre, 12=Mercier, 13=Rousseau, 14=van der Berg,
#                     15=Dubois, 16=Lambert, 17=Vermeulen, 18=Bouchard
#  19..26 IT/ES/PT:   19=Lombardi, 20=Moretti, 21=Mendoza, 22=Carvalho,
#                     23=García, 24=Romero, 25=Gonçalves, 26=Esposito
#  27..34 UK/IE/N:    27=O'Connor, 28=O'Sullivan, 29=Whitfield, 30=Lindqvist,
#                     31=Virtanen, 32=MacDonald, 33=Byrne, 34=Holmberg
#  35..42 NorthAm:    35=Martinez-Klein, 36=Patel-Johnson, 37=Goldstein,
#                     38=Thompson, 39=Carter, 40=Rivera, 41=Bennett, 42=Walker
#  43..48 LATAM:      43=Fernández, 44=Herrera, 45=Ramírez, 46=Vega,
#                     47=Cardoso, 48=Cruz
#  49..54 MENA/AF:    49=El Amrani, 50=Nkosi, 51=Hassan, 52=Mensah,
#                     53=Mansour, 54=Haddad
#  55..64 APAC:       55=Wang, 56=Tanaka, 57=Liu, 58=Park, 59=Huang, 60=Chen,
#                     61=Xu, 62=Nair, 63=Mehta, 64=Sato
#  65..67 Oceania:    65=Robertson, 66=O'Brien, 67=Whitmore
#  68..70 Reserves:   68=Boutros, 69=Reyes, 70=Albrecht

LEVELS_DE = [
    {
        "id": "l1",
        "name": "Strategische Ebene (Vorstand)",
        "roles": [
            {"id": "r1",  "name": "Vorsitz Krisenstab",                          "description": "Oberste Entscheidungsinstanz, Kommunikation mit Aufsichtsrat und Behördenleitung.", "critical": True,  "assignments": A(1, 2, 4)},
            {"id": "r2",  "name": "Stellvertretender Vorsitz",                   "description": "Übernimmt bei Ausfall des Vorsitzes, koordiniert Vorstandsanträge.",              "critical": True,  "assignments": A(2, 6, 1)},
            {"id": "r3",  "name": "Chief Communications Officer",                 "description": "Verantwortet die externe und interne Krisenkommunikation auf Vorstandsebene.",   "critical": True,  "assignments": A(3, 19, 27)},
            {"id": "r4",  "name": "General Counsel",                              "description": "Rechtsentscheidungen, Behördenkommunikation, Aufsichtsrats-Briefings.",          "critical": True,  "assignments": A(4, 20, 18)},
            {"id": "r5",  "name": "Chief Risk Officer",                           "description": "Bewertung Gesamtrisiko, Versicherungs-Notifikationen, Audit-Schnittstelle.",     "critical": False, "assignments": A(5, 29, 6)},
        ],
    },
    {
        "id": "l2",
        "name": "Taktische Krisenstabsleitung",
        "roles": [
            {"id": "r6",  "name": "Crisis Manager",                               "description": "Operative Gesamtleitung des Krisenstabs, Lagebild, Eskalation.",                 "critical": True,  "assignments": A(11, 14, 12)},
            {"id": "r7",  "name": "Deputy Crisis Manager",                        "description": "Stellvertretung Crisis Manager, Schichtwechsel-Koordination.",                  "critical": True,  "assignments": A(14, 11, 13)},
            {"id": "r8",  "name": "Head of Security",                              "description": "Leitung Security-Track, Schnittstelle CISO, Physical Security.",                "critical": True,  "assignments": A(12, 22, 35)},
            {"id": "r9",  "name": "Head of Business Continuity",                  "description": "Wiederanlauf-Priorisierung, BCM-Pläne aktivieren.",                              "critical": True,  "assignments": A(13, 44, 70)},
            {"id": "r10", "name": "Head of Crisis Communications",                "description": "Operative Comms, Statements, Pressekontakt, Sprachregelungen.",                  "critical": False, "assignments": A(19, 26, 38)},
            {"id": "r11", "name": "Crisis Staff Documentation",                   "description": "Lückenlose Protokollierung aller Entscheidungen und Lagewechsel.",               "critical": False, "assignments": A(58, 64, 7)},
        ],
    },
    {
        "id": "l3",
        "name": "Fachbereichsleitung",
        "roles": [
            {"id": "r12", "name": "Chief Information Security Officer (CISO)",   "description": "Cyber-Lagebild, Gesamtkoordination IT-Security-Maßnahmen.",                      "critical": True,  "assignments": A(22, 12, 36)},
            {"id": "r13", "name": "Head of IT Operations",                        "description": "Verfügbarkeit Infrastruktur, Wiederherstellung Services.",                       "critical": True,  "assignments": A(30, 10, 65)},
            {"id": "r14", "name": "Head of Application Development",              "description": "Bewertung Anwendungs-Impact, Patch- und Release-Notentscheidungen.",            "critical": False, "assignments": A(31, 17, 39)},
            {"id": "r15", "name": "Head of HR Crisis Response",                   "description": "Personelle Belastung, psychosoziale Unterstützung, externe Kommunikation MA.",   "critical": False, "assignments": A(7, 53, 48)},
            {"id": "r16", "name": "Head of Finance & Treasury",                   "description": "Zahlungsfähigkeit, Cash-Management, Versicherungs-Claims.",                      "critical": False, "assignments": A(29, 6, 5)},
            {"id": "r17", "name": "Head of Physical Security",                    "description": "Zugangsbeschränkungen, Site-Lockdown, externe Sicherheitsdienste.",              "critical": True,  "assignments": A(35, 51, 8)},
            {"id": "r18", "name": "Data Protection Officer (DPO)",                "description": "DSGVO-Meldewege, Aufsichtsbehörden, betroffene Personen.",                       "critical": True,  "assignments": A(28, 9, 49)},
            {"id": "r19", "name": "Head of Facilities",                           "description": "Räumlichkeiten, Backup-Standorte, Travel-Restriktionen.",                        "critical": False, "assignments": A(51, 8, 43)},
        ],
    },
    {
        "id": "l4",
        "name": "Operative Ebene",
        "roles": [
            {"id": "r20", "name": "SOC Shift Lead",                               "description": "Schichtführung im Security Operations Center, Triage, Eskalation.",              "critical": True,  "assignments": A(36, 24, 57)},
            {"id": "r21", "name": "Incident Response Lead",                       "description": "Containment, Eradication, Recovery — Fall-Owner pro Incident.",                  "critical": True,  "assignments": A(25, 41, 68)},
            {"id": "r22", "name": "Forensics Team Lead",                          "description": "Beweissicherung, Memory- und Disk-Forensik, Chain-of-Custody.",                   "critical": True,  "assignments": A(21, 15, 33)},
            {"id": "r23", "name": "Network Operations Lead",                      "description": "Segmentierung, Firewall-Änderungen, DNS-Pivots.",                                "critical": False, "assignments": A(37, 16, 47)},
            {"id": "r24", "name": "Endpoint Protection Lead",                     "description": "EDR-Steuerung, Isolation kompromittierter Endpoints, Re-Imaging.",                "critical": False, "assignments": A(43, 60, 50)},
            {"id": "r25", "name": "Threat Intelligence Lead",                     "description": "IoC-Verteilung, Attribution, externe Feeds.",                                    "critical": False, "assignments": A(40, 55, 25)},
            {"id": "r26", "name": "Vulnerability Management Lead",                "description": "Notfall-Patching, Priorisierung Exploit-aktive CVEs.",                            "critical": False, "assignments": A(49, 63, 10)},
            {"id": "r27", "name": "IT Recovery Lead",                             "description": "Restore aus Backups, Wiederanlauf-Reihenfolge, Datenintegrität.",                 "critical": True,  "assignments": A(70, 42, 52)},
            {"id": "r28", "name": "Communications Operations Lead",               "description": "Operative Comms-Umsetzung, Multi-Channel-Verteilung, Sprachen.",                  "critical": False, "assignments": A(38, 46, 59)},
        ],
    },
]

# English mirror — same IDs and same person assignments as LEVELS_DE.
LEVELS_EN = [
    {
        "id": "l1",
        "name": "Strategic Level (Executive Board)",
        "roles": [
            {"id": "r1",  "name": "Crisis Committee Chair",                       "description": "Top decision authority; liaison with supervisory board and regulators.",            "critical": True,  "assignments": A(1, 2, 4)},
            {"id": "r2",  "name": "Deputy Chair",                                  "description": "Acts when the Chair is unavailable; coordinates board proposals.",                "critical": True,  "assignments": A(2, 6, 1)},
            {"id": "r3",  "name": "Chief Communications Officer",                 "description": "Owns external and internal crisis communications at board level.",                "critical": True,  "assignments": A(3, 19, 27)},
            {"id": "r4",  "name": "General Counsel",                              "description": "Legal calls, regulator communications, supervisory board briefings.",            "critical": True,  "assignments": A(4, 20, 18)},
            {"id": "r5",  "name": "Chief Risk Officer",                           "description": "Overall risk evaluation, insurance notifications, audit interface.",              "critical": False, "assignments": A(5, 29, 6)},
        ],
    },
    {
        "id": "l2",
        "name": "Tactical Crisis Command",
        "roles": [
            {"id": "r6",  "name": "Crisis Manager",                               "description": "Operational command of the crisis team; situational picture; escalation.",        "critical": True,  "assignments": A(11, 14, 12)},
            {"id": "r7",  "name": "Deputy Crisis Manager",                        "description": "Stands in for the Crisis Manager; coordinates shift handovers.",                  "critical": True,  "assignments": A(14, 11, 13)},
            {"id": "r8",  "name": "Head of Security",                              "description": "Owns the security track; interface to CISO and Physical Security.",               "critical": True,  "assignments": A(12, 22, 35)},
            {"id": "r9",  "name": "Head of Business Continuity",                  "description": "Recovery prioritisation; activates BCM playbooks.",                                "critical": True,  "assignments": A(13, 44, 70)},
            {"id": "r10", "name": "Head of Crisis Communications",                "description": "Operational comms, statements, press contact, language rules.",                    "critical": False, "assignments": A(19, 26, 38)},
            {"id": "r11", "name": "Crisis Staff Documentation",                   "description": "Gap-free logging of all decisions and situation changes.",                         "critical": False, "assignments": A(58, 64, 7)},
        ],
    },
    {
        "id": "l3",
        "name": "Functional Leadership",
        "roles": [
            {"id": "r12", "name": "Chief Information Security Officer (CISO)",   "description": "Cyber situational picture; overall coordination of IT-security actions.",         "critical": True,  "assignments": A(22, 12, 36)},
            {"id": "r13", "name": "Head of IT Operations",                        "description": "Infrastructure availability; service restoration.",                                "critical": True,  "assignments": A(30, 10, 65)},
            {"id": "r14", "name": "Head of Application Development",              "description": "Application impact assessment; patch and release-stop decisions.",                 "critical": False, "assignments": A(31, 17, 39)},
            {"id": "r15", "name": "Head of HR Crisis Response",                   "description": "Workforce load, psycho-social support, employee communications.",                  "critical": False, "assignments": A(7, 53, 48)},
            {"id": "r16", "name": "Head of Finance & Treasury",                   "description": "Liquidity, cash management, insurance claims.",                                    "critical": False, "assignments": A(29, 6, 5)},
            {"id": "r17", "name": "Head of Physical Security",                    "description": "Access restrictions, site lockdown, external security services.",                  "critical": True,  "assignments": A(35, 51, 8)},
            {"id": "r18", "name": "Data Protection Officer (DPO)",                "description": "GDPR notifications, supervisory authorities, affected individuals.",               "critical": True,  "assignments": A(28, 9, 49)},
            {"id": "r19", "name": "Head of Facilities",                           "description": "Premises, backup sites, travel restrictions.",                                     "critical": False, "assignments": A(51, 8, 43)},
        ],
    },
    {
        "id": "l4",
        "name": "Operational Level",
        "roles": [
            {"id": "r20", "name": "SOC Shift Lead",                               "description": "Security Operations Center shift command; triage; escalation.",                    "critical": True,  "assignments": A(36, 24, 57)},
            {"id": "r21", "name": "Incident Response Lead",                       "description": "Containment, eradication, recovery — case owner per incident.",                    "critical": True,  "assignments": A(25, 41, 68)},
            {"id": "r22", "name": "Forensics Team Lead",                          "description": "Evidence preservation, memory and disk forensics, chain-of-custody.",              "critical": True,  "assignments": A(21, 15, 33)},
            {"id": "r23", "name": "Network Operations Lead",                      "description": "Segmentation, firewall changes, DNS pivots.",                                      "critical": False, "assignments": A(37, 16, 47)},
            {"id": "r24", "name": "Endpoint Protection Lead",                     "description": "EDR steering, isolation of compromised endpoints, re-imaging.",                    "critical": False, "assignments": A(43, 60, 50)},
            {"id": "r25", "name": "Threat Intelligence Lead",                     "description": "IoC distribution, attribution, external feeds.",                                    "critical": False, "assignments": A(40, 55, 25)},
            {"id": "r26", "name": "Vulnerability Management Lead",                "description": "Emergency patching, prioritisation of actively-exploited CVEs.",                    "critical": False, "assignments": A(49, 63, 10)},
            {"id": "r27", "name": "IT Recovery Lead",                             "description": "Restore from backups, recovery order, data integrity.",                             "critical": True,  "assignments": A(70, 42, 52)},
            {"id": "r28", "name": "Communications Operations Lead",               "description": "Operational comms delivery, multi-channel distribution, languages.",                "critical": False, "assignments": A(38, 46, 59)},
        ],
    },
]


# ---------------------------------------------------------------------------
# 5 skill-based pools, all attached to operative-level lead roles (level l4)
# Each pool has lead + 5-8 members, mix of regions
# ---------------------------------------------------------------------------

# Pool memberships — chosen for plausible skill match with each person's
# keywords. IDs match the persons array (see PERSONS list).
# - SOC pool: people with SOC / Threat-Hunting / Tier-2 keywords
# - Forensics pool: people with Forensics / Malware / Memory Analysis
# - Crisis Comms pool: Comms / Media / Customer Care / Internal
# - IT-Recovery pool: Recovery / Backup / DR-Lead / IT-Operations
# - Legal Response pool: Legal / Privacy / Compliance / DPO

POOLS_DE = [
    {
        "id":           "pool-soc-analysts",
        "name":         "SOC-Analysten",
        "leadRoleId":   "r20",   # SOC Shift Lead
        "memberIds":    ["p23", "p24", "p32", "p36", "p40", "p41", "p46", "p54", "p57", "p66"],
        "notes":        "Analystenpool für SOC-Schichten weltweit. Tier-1/Tier-2-Mischung, Threat-Hunting-Erfahrung.",
        "secondaryLeadRoleIds": ["r25"],
    },
    {
        "id":           "pool-forensics",
        "name":         "Forensik-Spezialisten",
        "leadRoleId":   "r22",   # Forensics Team Lead
        "memberIds":    ["p15", "p21", "p33", "p39", "p45", "p56", "p60", "p61", "p62"],
        "notes":        "Memory-, Disk- und Netzwerk-Forensik. Chain-of-Custody-zertifiziert.",
        "secondaryLeadRoleIds": [],
    },
    {
        "id":           "pool-crisis-comms",
        "name":         "Krisenkommunikation",
        "leadRoleId":   "r28",   # Communications Operations Lead
        "memberIds":    ["p3", "p19", "p26", "p38", "p48", "p59", "p64"],
        "notes":        "Mehrsprachiger Comms-Pool. Statements, Übersetzungen, Social-Media-Monitoring.",
        "secondaryLeadRoleIds": ["r10"],
    },
    {
        "id":           "pool-it-recovery",
        "name":         "IT-Recovery",
        "leadRoleId":   "r27",   # IT Recovery Lead
        "memberIds":    ["p10", "p30", "p34", "p42", "p52", "p67", "p70"],
        "notes":        "Restore aus Backups, DR-Wiederanlauf, Datenintegritäts-Prüfung.",
        "secondaryLeadRoleIds": [],
    },
    {
        "id":           "pool-legal-response",
        "name":         "Legal-Response",
        "leadRoleId":   "r18",   # DPO (l3) — Pool darf level-übergreifend referenzieren
        "memberIds":    ["p9", "p18", "p20", "p28", "p49", "p53", "p69"],
        "notes":        "Datenschutz, Vertragsrecht, Regulator-Kommunikation. Mehrsprachig.",
        "secondaryLeadRoleIds": ["r4"],
    },
]

POOLS_EN = [
    {
        "id":           "pool-soc-analysts",
        "name":         "SOC Analysts",
        "leadRoleId":   "r20",
        "memberIds":    ["p23", "p24", "p32", "p36", "p40", "p41", "p46", "p54", "p57", "p66"],
        "notes":        "Analyst pool for SOC shifts worldwide. Tier-1/Tier-2 mix, threat-hunting experience.",
        "secondaryLeadRoleIds": ["r25"],
    },
    {
        "id":           "pool-forensics",
        "name":         "Forensics Specialists",
        "leadRoleId":   "r22",
        "memberIds":    ["p15", "p21", "p33", "p39", "p45", "p56", "p60", "p61", "p62"],
        "notes":        "Memory, disk and network forensics. Chain-of-custody certified.",
        "secondaryLeadRoleIds": [],
    },
    {
        "id":           "pool-crisis-comms",
        "name":         "Crisis Communications",
        "leadRoleId":   "r28",
        "memberIds":    ["p3", "p19", "p26", "p38", "p48", "p59", "p64"],
        "notes":        "Multilingual comms pool. Statements, translations, social-media monitoring.",
        "secondaryLeadRoleIds": ["r10"],
    },
    {
        "id":           "pool-it-recovery",
        "name":         "IT Recovery",
        "leadRoleId":   "r27",
        "memberIds":    ["p10", "p30", "p34", "p42", "p52", "p67", "p70"],
        "notes":        "Restore from backups, DR re-start, data-integrity verification.",
        "secondaryLeadRoleIds": [],
    },
    {
        "id":           "pool-legal-response",
        "name":         "Legal Response",
        "leadRoleId":   "r18",
        "memberIds":    ["p9", "p18", "p20", "p28", "p49", "p53", "p69"],
        "notes":        "Data protection, contract law, regulator communications. Multilingual.",
        "secondaryLeadRoleIds": ["r4"],
    },
]


# ---------------------------------------------------------------------------
# Runtime state — one anchor absence to demonstrate the cascade
# (Head of Physical Security p32 is away; deputy p12 steps in)
# ---------------------------------------------------------------------------

RUNTIME = {
    # Anchor absence to demonstrate the cascade on the chart and overview:
    # p35 Jennifer Martinez-Klein is Primary for r17 (Head of Physical
    # Security). With her unavailable, p51 Amina Hassan steps in.
    "unavailable": {
        "p35": True,
    },
    "manualAssignments": {},
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def build_export(meta, levels, pools):
    persons = build_persons()
    cfg = {
        "schemaVersion": 3,
        "meta": meta,
        "persons": persons,
        "levels": levels,
        "pools": pools,
    }
    export = {
        "format": "cram-export",
        "formatVersion": 1,
        "appVersion": "2.2.0-rc1",
        "exportedAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "config": cfg,
        "runtime": RUNTIME,
    }
    return export


def validate(export):
    """Sanity checks: all personIds + leadRoleIds resolve."""
    cfg = export["config"]
    person_ids = {p["id"] for p in cfg["persons"]}
    role_ids = set()
    for lvl in cfg["levels"]:
        for r in lvl["roles"]:
            role_ids.add(r["id"])
            for a in r["assignments"]:
                if a["personId"] not in person_ids:
                    raise ValueError(f"Role {r['id']} references missing person {a['personId']}")
    for pool in cfg["pools"]:
        if pool["leadRoleId"] and pool["leadRoleId"] not in role_ids:
            raise ValueError(f"Pool {pool['id']} references missing leadRoleId {pool['leadRoleId']}")
        for mid in pool["memberIds"]:
            if mid not in person_ids:
                raise ValueError(f"Pool {pool['id']} references missing person {mid}")
        for sid in pool.get("secondaryLeadRoleIds", []):
            if sid not in role_ids:
                raise ValueError(f"Pool {pool['id']} secondary references missing role {sid}")
    for pid in export["runtime"]["unavailable"].keys():
        if pid not in person_ids:
            raise ValueError(f"Runtime references missing person {pid}")
    return True


def main():
    out_dir = Path(__file__).resolve().parent.parent / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_de = {
        "organizationName": "Globale Enterprise AG — Konzernkrisenstab",
        "printTitle":       "Konzernkrisenstab — Rollen und Vertretungen",
        "lastModified":     dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    meta_en = {
        "organizationName": "Global Enterprise Corp. — Corporate Crisis Committee",
        "printTitle":       "Corporate Crisis Committee — Roles and Substitutions",
        "lastModified":     dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    de = build_export(meta_de, LEVELS_DE, POOLS_DE)
    en = build_export(meta_en, LEVELS_EN, POOLS_EN)

    validate(de)
    validate(en)

    de_path = out_dir / "cram-demo-enterprise-de.json"
    en_path = out_dir / "cram-demo-enterprise-en.json"
    de_path.write_text(json.dumps(de, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    en_path.write_text(json.dumps(en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    n_persons = len(de["config"]["persons"])
    n_roles = sum(len(lvl["roles"]) for lvl in de["config"]["levels"])
    n_pools = len(de["config"]["pools"])
    print(f"OK — wrote {de_path.name} and {en_path.name}")
    print(f"     {n_persons} persons, {len(LEVELS_DE)} levels, {n_roles} roles, {n_pools} pools")


if __name__ == "__main__":
    main()
