# экспертный календарь Валерия (14.09.2026) — id турниров из calendar.html
import gd_data as g
W={}
def setw(name_part, w):
    for t in g.CAL['tournaments']:
        if name_part.lower() in t['name'].lower() and t['start']>'2026-09-14': W[t['id']]=w
for n,w in (('Red Syndicate',0.5),('DarKStadt',0.3),('Israel Open',0.4),('Novi Sad',0.4),('Warsaw Mafia Open',0.3),('Sova',0.3),
            ('4th Month',0.4),('EdelweISS',0.3),('Tbilisoba',0.4),('Чемпионат Молдовы',1.5),('Valencia',0.6),('Central Cup',1.5),('Командный Чемпионат Польши',0.6),
            ('Mediterranean',1.6),('Black circle',1.4),('Atlantic',0.3),('Круг избранных',0.3),('Белграда',0.3),('Wroclaw Mafia Open',0.7),('Krakow',0.7),('Dutch Open',0.8),
            ('Black&Red',0.3),('Lodz Mafia Open',0.5),('Prague Cup',0.7),('Cyprus Open 26: Wint',1.5),('КАНОничный',0.4),('Madrid',0.4)):
    setw(n,w)
