# Description

We will use the OBB to determine what is the front and back.
- Generic Mode
- Above or Below Mode
- Side Mode
- Front or Back Mode


For all those possibilties, we can determine some volume to create exclusion zone.

In front is very subjective, we can only determine the front and the back of an object. 
The front is considered as the largest part of the object. 




Generic Mode
Check all distance between the OBB and the object.

Above Or Below - Specific Rule
The source object must be above or below the object. 



Right Above and Right Below - Specific Rule
The source ob

Side Mode - Specific rule
The object must to be above, nor be below. It must be on the side 




DEV NOTE
Il faut créer plusieurs règles pour chaque mode. La détermination de ce qu'est le devant, le haut etc va être chiant à généraliser. 
Autant faire des fonctions différentes.

La OBB forme un objet uniforme afin d'y lancer plusieurs calculs configurables à l'avance. 
Devant
A Côté
Au dessus

20cm du bas
20cm du haut
20cm des côtés 

1m devant et etendu de 20cm vers le haut. 
1m devant, forme de porte, en arc de cercle. Ouverture à 120degrés. 

1m devant, en forme de double porte
Pour une poutre, 10cm du bord en haut et 20cm sur le côté. Une zone libre au centre. 
Pour une fenêtre avec une allège, devant mais pas jusque en haut. 
Pour une prise pompier, un cone qui part d'une surface spécifique. 



# Property

# Result


# Example
This rule can check if an object is in front of a door that could prevent the opening.
