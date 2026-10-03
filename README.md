# Simulateur de chauffage de l'acétone

Application web locale permettant de simuler la séparation d'un débit d'acétone, puis le chauffage et la vaporisation du deuxième courant.

## Fonctionnalités

- réglage du débit, de la température d'alimentation et de la pression ;
- réglage des fractions des deux courants avec validation de leur somme ;
- calcul de la température d'ébullition par l'équation d'Antoine ;
- calcul des chaleurs sensible, latente et totale ;
- calcul du duty thermique et de la puissance ;
- vérification du bilan massique ;
- courbe et tableau pression/température d'ébullition.

## Installation

Depuis le dossier `acetone_simulator` :

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre ensuite dans le navigateur à l'adresse locale indiquée par Streamlit.

## Organisation

- `app.py` : interface web et affichage des résultats ;
- `calculations.py` : constantes, équations et calculs scientifiques ;
- `requirements.txt` : dépendances Python du projet.

## Modèle de calcul

Les calculs utilisent les paramètres d'Antoine fournis pour la pression de vapeur, une capacité calorifique liquide linéaire en température et la corrélation fournie pour l'enthalpie de vaporisation. Seul le courant 2 est chauffé et vaporisé.
