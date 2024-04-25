# REST-API
Application Web responsable du paiement de commandes Internet

Pour lancer l'app : docker run -p 5000:5000 nomConteneur

L'initialisation de la base de donnees est faite automatiquement au lancement de l'application.
Toutes les variables d'environnement sont deja initialisees dans le dockerfile mais vous pouvez les changer au besoin.
Le front end est disponible à partir des routes /web/
Nous n'avons pas reussi à implementer les workers.