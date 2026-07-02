# ⚖️ AUDIT JURIDIQUE — Operator Roster / Import System

> Généré par **openai/gpt-5.5-20260423** via OpenRouter.
> Date : 2026-06-20 · Audit de conformité bêta + lancement public.
> **NOTE** : Audit de conformité par juriste-conseil. Ne remplace pas un avocat
> commis pour un cas individuel. Document de travail pour prioriser les actions.

---

## 🔴 SYNTHÈSE EXÉCUTIVE

- **Risque global : ÉLEVÉ** — non pas à cause de la waitlist ou du RGPD, mais à cause de l’usage commercial de **transcripts YouTube de tiers** comme base de connaissance monétisée : c’est le point qui peut déclencher une vraie réclamation avant même une sanction administrative.

- **Les 3 actions juridiques à faire en premier avant la bêta :**
  1. **Geler l’usage des transcripts bruts YouTube** dans le produit vendu / Roster tant que les droits ne sont pas clarifiés ou licenciés.
  2. **Remplacer la base actuelle par des notes internes originales et non verbatim**, sourcées par URL, avec citations très courtes uniquement si nécessaires.
  3. **Mettre en place un socle légal minimum avant collecte/facturation** : mentions légales LCEN, politique de confidentialité, CGV/CGU, preuve de consentement email, disclaimer renforcé “outil d’aide à la décision”.

---

## 📋 AUDIT DÉTAILLÉ PAR POINT

---

# POINT 1 — DROITS D’AUTEUR SUR LES TRANSCRIPTS YOUTUBE

## Diagnostic

### a) Statut juridique d’un transcript YouTube

Un transcript YouTube peut être juridiquement analysé à plusieurs niveaux :

1. **La vidéo YouTube elle-même**  
   Une vidéo est généralement une œuvre audiovisuelle protégée par le droit d’auteur si elle est originale.  
   Articles pertinents :  
   - **CPI, art. L112-2** : sont notamment protégées les œuvres audiovisuelles, conférences, allocutions, sermons, plaidoiries et autres œuvres de même nature.  
   - **CPI, art. L111-1** : l’auteur jouit d’un droit de propriété incorporelle exclusif et opposable à tous.

2. **Le discours oral contenu dans la vidéo**  
   Le propos oral peut être protégé s’il porte l’empreinte de la personnalité de son auteur : structure, ton, choix des exemples, pédagogie, formulation, séquence argumentative.  
   Les idées, méthodes, données factuelles, prix, ratios ou concepts business ne sont pas protégés en eux-mêmes. Mais **leur expression structurée** peut l’être.

3. **Le transcript brut**  
   Le transcript n’est pas forcément une œuvre originale distincte s’il est généré automatiquement. En revanche, il constitue très souvent une **reproduction textuelle** d’une œuvre orale/audiovisuelle protégée.  
   Le fait de copier, stocker et réutiliser ce transcript peut donc être une reproduction non autorisée.  
   Article central :  
   - **CPI, art. L122-4** : toute représentation ou reproduction intégrale ou partielle faite sans le consentement de l’auteur ou de ses ayants droit est illicite.

4. **Les synthèses dérivées**  
   Les fichiers `.md` de synthèse peuvent être licites s’ils extraient uniquement des idées, informations factuelles et enseignements généraux.  
   Ils deviennent risqués s’ils reprennent :
   - la structure pédagogique originale ;
   - des formulations caractéristiques ;
   - des exemples propres au créateur ;
   - une séquence argumentative reconnaissable ;
   - des passages paraphrasés massivement.

**Conclusion :** le transcript brut est le point le plus dangereux. Même si le texte auto-généré n’est pas original en lui-même, il reproduit une œuvre potentiellement protégée.

---

### b) Conditions d’utilisation YouTube et extraction via yt-dlp

L’extraction de transcripts via des outils tiers type `yt-dlp` pose deux problèmes.

#### 1. Problème contractuel : CGU YouTube

Les conditions YouTube interdisent généralement :
- l’accès au contenu autrement que via les fonctionnalités autorisées du service ;
- l’usage de moyens automatisés pour accéder, collecter ou extraire du contenu ;
- la copie, reproduction, distribution ou exploitation du contenu sans autorisation.

Le risque principal ici n’est pas forcément une action judiciaire de YouTube. Le risque réel est plutôt :
- blocage IP / compte ;
- réclamation d’un créateur ;
- signalement DMCA / copyright ;
- mise en demeure ;
- atteinte réputationnelle si le projet est présenté comme construit sur les contenus de YouTubeurs tiers.

#### 2. Contournement de mesure technique ?

En droit français, les mesures techniques de protection sont protégées.  
Articles pertinents :
- **CPI, art. L331-5** : protection des mesures techniques efficaces destinées à empêcher ou limiter les utilisations non autorisées.
- **CPI, art. L335-3-1** : sanction de l’atteinte aux mesures techniques.

Si les transcripts sont publiquement accessibles sans contournement d’un accès payant, d’un DRM ou d’une restriction technique forte, le risque de qualification comme contournement de mesure technique est **moins évident**.  
En revanche, si l’outil contourne des restrictions, signatures, limitations d’accès, protections anti-scraping ou restrictions de l’API, le risque augmente.

**Risque réel :** violation des CGU + droit d’auteur, davantage que contournement technique.

---

### c) Exception de courte citation — CPI, art. L122-5, 3°

L’exception de citation permet certaines reproductions sans autorisation, mais dans des conditions strictes.

Article pertinent :
- **CPI, art. L122-5, 3° a)** : lorsque l’œuvre a été divulguée, l’auteur ne peut interdire les analyses et courtes citations justifiées par leur caractère critique, polémique, pédagogique, scientifique ou d’information, sous réserve de l’indication claire du nom de l’auteur et de la source.

Conditions cumulatives :
- citation courte ;
- proportionnée ;
- justifiée par un but critique, pédagogique, scientifique ou d’information ;
- intégrée dans une œuvre seconde autonome ;
- attribution claire de l’auteur et de la source.

Dans votre cas, les synthèses longues et structurées utilisées comme base d’un système IA monétisé ne relèvent pas naturellement de la courte citation.

Pourquoi :
- 24h+ de transcripts ;
- 40 fichiers ;
- usage systématique ;
- base de connaissance opérationnelle ;
- monétisation indirecte via cours et abonnement ;
- reformulation longue, pas simple citation ponctuelle.

**Conclusion :** l’exception de courte citation ne couvre pas l’architecture actuelle.

---

### d) Droits patrimoniaux vs droits moraux

Même si un YouTubeur donne son accord, il faut distinguer :

#### Droits patrimoniaux
Ce sont les droits économiques :
- reproduction ;
- représentation ;
- adaptation ;
- traduction ;
- incorporation dans un système logiciel ;
- exploitation commerciale.

Articles pertinents :
- **CPI, art. L122-1** : droit d’exploitation appartenant à l’auteur.
- **CPI, art. L122-4** : reproduction/représentation sans consentement illicite.
- **CPI, art. L131-3** : la transmission des droits doit être précise : droits cédés, durée, territoire, destination, rémunération.

#### Droits moraux
Ils demeurent attachés à l’auteur.
Article pertinent :
- **CPI, art. L121-1** : droit au respect du nom, de la qualité et de l’œuvre ; droit moral perpétuel, inaliénable et imprescriptible.

Conséquence pratique :
- l’attribution doit être claire ;
- ne pas laisser croire que le YouTubeur cautionne le produit ;
- éviter les reformulations qui dénaturent son propos ;
- prévoir une clause permettant au créateur de demander retrait/correction en cas d’atteinte à son image ou à son œuvre.

**Important :** l’attribution seule ne remplace jamais une autorisation d’exploitation.

---

### e) Sanctions encourues

#### Sanctions théoriques

La contrefaçon est à la fois :
- une faute civile ;
- potentiellement un délit pénal.

Articles pertinents :
- **CPI, art. L335-2** : contrefaçon punie de 3 ans d’emprisonnement et 300 000 € d’amende.
- **CPI, art. L335-3** : est également un délit de contrefaçon toute reproduction, représentation ou diffusion d’une œuvre de l’esprit en violation des droits de l’auteur.
- **CPI, art. L331-1-3** : dommages-intérêts civils prenant en compte les conséquences économiques négatives, le préjudice moral et les bénéfices réalisés par le contrefacteur.

#### Sanctions probables en pratique

Pour une bêta fermée, le risque pénal pur est faible.  
Le risque réel est plutôt :

- mise en demeure d’un créateur ;
- demande de retrait immédiat ;
- demande de rémunération/licence ;
- réclamation publique sur YouTube/Twitter/LinkedIn ;
- signalement copyright ;
- blocage d’un lancement ;
- action civile si le projet génère des revenus significatifs ;
- accusation de parasitisme ou concurrence déloyale si vous vous positionnez contre ces mêmes créateurs.

**Risque réel : ÉLEVÉ**, car le projet cite explicitement des YouTubeurs concurrents et monétise un système construit sur leurs contenus.

---

## Niveau de risque

### RISQUE ÉLEVÉ — à régler avant lancement bêta

Probabilité réelle : **forte à moyenne**, selon visibilité du lancement.  
Un créateur qui découvre que ses transcripts sont utilisés pour alimenter un produit payant peut réagir rapidement.

---

## Correction concrète

Actions immédiates :

1. **Supprimer les transcripts bruts du produit distribué et de l’environnement de prod**
   - Pas de fichiers `.txt` accessibles.
   - Pas d’affichage de passages verbatim.
   - Pas de RAG direct sur transcripts non autorisés.

2. **Créer une base de connaissance “notes internes originales”**
   - Notes rédigées par l’équipe.
   - Pas de copier-coller.
   - Pas de paraphrase longue.
   - Sources citées en bibliographie : titre vidéo, URL, date de consultation.
   - Extraction uniquement des idées, données factuelles et enseignements.

3. **Limiter les citations**
   - Citations très courtes.
   - Uniquement pour illustrer un point critique.
   - Attribution systématique.
   - Pas de citation utilisée comme matière première principale.

4. **Contacter les 7 chaînes**
   - Demander une licence écrite.
   - Expliquer usage : synthèse, agents IA, cours, abonnement.
   - Prévoir droit de retrait raisonnable.
   - Prévoir attribution.
   - Prévoir territoire, durée, supports, rémunération ou gratuité.

5. **Ne pas invoquer le “fair use”**
   - Le fair use américain n’est pas applicable comme défense générale en France.
   - En France, seules les exceptions prévues par le CPI sont pertinentes, notamment **CPI, art. L122-5**.

---

# POINT 2 — RGPD / COLLECTE EMAIL WAITLIST

## Diagnostic

La landing actuelle est mieux positionnée qu’une landing agressive classique. Elle indique :
- finalité ;
- base légale ;
- absence de revente ;
- durée jusqu’au désabonnement ;
- droit d’accès, rectification, effacement, opposition.

Mais elle reste insuffisante pour un lancement public, et encore incomplète même pour une bêta si l’email est réellement collecté côté serveur.

Articles pertinents :
- **RGPD, art. 5** : principes de licéité, loyauté, transparence, minimisation, limitation de conservation.
- **RGPD, art. 6.1.a** : consentement.
- **RGPD, art. 7** : conditions du consentement et preuve.
- **RGPD, art. 12 à 14** : information des personnes.
- **RGPD, art. 28** : sous-traitants.
- **RGPD, art. 30** : registre des traitements, sauf exemption limitée.
- **RGPD, art. 32** : sécurité.
- **RGPD, art. 44 et s.** : transferts hors UE.
- **Loi Informatique et Libertés** modifiée.
- Recommandations CNIL sur cookies/traceurs et prospection.

---

## a) Mention actuelle suffisante ?

### Pour bêta fermée 30-100 inscrits

**Risque MOYEN**, mais acceptable si corrigé légèrement avant ouverture.

Il manque surtout :
- identité réelle de l’éditeur ;
- email de contact ;
- lien vers une politique de confidentialité complète ;
- mécanisme réel de désabonnement ;
- preuve de consentement ;
- mention CNIL ;
- mention des sous-traitants si ConvertKit/Buttondown est utilisé.

### Pour lancement public 1000+

**Insuffisant.**

Il faudra :
- politique de confidentialité dédiée ;
- mentions légales complètes ;
- gestion du consentement horodaté ;
- registre des traitements ;
- DPA avec prestataires ;
- analyse transferts hors UE ;
- sécurité et purge des données ;
- process d’exercice des droits.

---

## b) Éléments manquants

À ajouter avant bêta :

1. **Identité de l’éditeur**
   - nom ou dénomination sociale ;
   - forme sociale ;
   - SIRET/RCS si société ou entrepreneur déclaré ;
   - adresse ;
   - email de contact.

2. **Contact vie privée**
   - adresse email dédiée : `privacy@...` ou équivalent.

3. **Hébergeur**
   - nom ;
   - adresse ;
   - contact.

4. **Politique de confidentialité séparée**
   Elle doit préciser :
   - responsable du traitement ;
   - finalités ;
   - base légale ;
   - données collectées ;
   - source des données ;
   - destinataires ;
   - sous-traitants ;
   - transferts hors UE ;
   - durée de conservation ;
   - droits RGPD ;
   - droit d’introduire une réclamation auprès de la CNIL ;
   - modalités de retrait du consentement.

5. **Consentement horodaté**
   À conserver :
   - email ;
   - date/heure ;
   - source/formulaire ;
   - version de la mention ;
   - IP éventuellement, avec prudence ;
   - statut opt-in/désabonnement.

6. **Sous-traitants**
   Si ConvertKit, Buttondown, Mailchimp, Brevo, Formspree, Vercel, Netlify, etc. :
   - DPA / accord de sous-traitance ;
   - localisation des données ;
   - mesures de sécurité ;
   - transferts hors UE.

---

## c) localStorage = collecte ? Faut-il un bandeau cookies ?

Le `localStorage` est un stockage dans le terminal de l’utilisateur. Il entre dans le champ des règles ePrivacy/cookies lorsque le site lit ou écrit une information dans le terminal.

En France, la règle vient notamment de :
- **Loi Informatique et Libertés, art. 82** ;
- doctrine CNIL cookies/traceurs.

Ici, le script stocke localement :

```js
localStorage.setItem('roster_email', em.value);
```

Analyse pratique :

- Si c’est uniquement une démo locale et que l’email n’est pas transmis au serveur, l’éditeur ne collecte pas réellement l’email côté back-end.
- Mais le site écrit quand même une donnée personnelle dans le terminal.
- Si ce stockage est strictement nécessaire pour rendre le service demandé par l’utilisateur, le consentement cookies séparé n’est pas forcément nécessaire.
- En revanche, stocker l’email en clair dans `localStorage` est une mauvaise pratique de sécurité et de minimisation.

Correction :
- ne pas stocker l’email en localStorage ;
- afficher simplement un message de confirmation ;
- envoyer l’email au backend ou prestataire conforme ;
- si localStorage utilisé pour préférences strictement nécessaires, le mentionner dans la politique de confidentialité/cookies.

**Bandeau cookies :** pas nécessaire si aucun cookie/traceur non essentiel, pas d’analytics, pas de pixels marketing, pas de retargeting.  
Il devient nécessaire pour analytics non exemptés, pixels Meta/Google, tracking publicitaire, affiliation.

---

## d) ConvertKit / Buttondown : obligations

Si vous branchez ConvertKit ou Buttondown, ces prestataires deviennent des **sous-traitants** au sens du RGPD.

Article pertinent :
- **RGPD, art. 28** : le traitement par un sous-traitant doit être régi par un contrat ou autre acte juridique.

À vérifier :
- DPA disponible ;
- lieu d’hébergement ;
- sous-traitants ultérieurs ;
- sécurité ;
- assistance en cas d’exercice de droits ;
- suppression/export des données ;
- transfert hors UE.

Si prestataire américain :
- vérifier s’il est certifié **EU-US Data Privacy Framework** ;
- sinon clauses contractuelles types + analyse de transfert ;
- articles pertinents : **RGPD, art. 44 à 49**.

---

## e) Risque concret bêta vs lancement public

### Bêta fermée 30-100 inscrits

**Risque réel : FAIBLE à MOYEN**, si :
- pas de spam ;
- consentement clair ;
- désabonnement facile ;
- pas de revente ;
- pas de tracking publicitaire ;
- peu de données collectées.

Le risque CNIL/DGCCRF est limité, sauf plainte d’un utilisateur ou pratiques agressives.

### Lancement public 1000+

**Risque MOYEN**, voire ÉLEVÉ si :
- emails non consentis ;
- absence de désabonnement ;
- absence d’identité éditeur ;
- promesses marketing trompeuses ;
- tracking publicitaire sans consentement ;
- prestataires US non encadrés.

---

## Sanctions théoriques vs probables

Sanctions théoriques :
- jusqu’à **20 M€ ou 4 % du CA mondial** pour les manquements les plus graves : **RGPD, art. 83**.

Sanctions probables :
- demande de mise en conformité ;
- avertissement ;
- plainte utilisateur ;
- blocage par prestataire email ;
- mauvaise réputation ;
- faible probabilité d’amende CNIL en bêta fermée si bonne foi et faible volume.

---

## Correction concrète

Avant bêta :
- remplacer localStorage par vrai opt-in email ;
- ajouter case ou wording clair de consentement ;
- conserver preuve du consentement ;
- ajouter politique de confidentialité séparée ;
- ajouter mentions légales complètes ;
- utiliser un outil email avec DPA ;
- intégrer lien de désabonnement dans chaque email ;
- ne pas ajouter d’analytics non essentiels sans gestion cookies.

---

# POINT 3 — RESPONSABILITÉ CIVILE / CONSEIL

## Diagnostic

Le disclaimer actuel est utile mais insuffisant. Il réduit l’ambiguïté, mais ne neutralise pas :
- la responsabilité contractuelle ;
- les pratiques commerciales trompeuses ;
- l’obligation d’information ;
- les erreurs manifestes des agents ;
- les promesses commerciales trop précises.

Articles pertinents :
- **Code civil, art. 1231-1** : responsabilité contractuelle en cas d’inexécution ou mauvaise exécution.
- **Code civil, art. 1240 et 1241** : responsabilité délictuelle pour faute, négligence ou imprudence.
- **Code de la consommation, art. L111-1** : obligation précontractuelle d’information.
- **Code de la consommation, art. L121-2 et L121-3** : pratiques commerciales trompeuses par action ou omission.
- **Code de la consommation, art. R212-1 et R212-2** : clauses abusives dans les contrats consommateurs.
- **Code de la consommation, art. L221-5 et suivants** : vente à distance.
- **Code de la consommation, art. L224-25-1 et suivants** : contenus et services numériques.

---

## a) Le disclaimer “pas un conseil personnalisé” protège-t-il vraiment ?

Il protège partiellement.

Il est utile pour démontrer :
- que le produit est un outil d’aide à la décision ;
- que l’utilisateur doit faire valider par des professionnels ;
- que les chiffres sont estimatifs ;
- qu’aucun résultat n’est garanti.

Mais il ne protège pas si :
- les agents donnent des affirmations catégoriques ;
- les pages de vente promettent un résultat économique ;
- le produit présente des codes HS ou certifications comme “validés” ;
- les erreurs sont répétées ou prévisibles ;
- les sources sont insuffisamment vérifiées ;
- l’utilisateur est consommateur et la clause tente d’exclure toute responsabilité.

À éviter :
- “code HS validé” ;
- “conforme CE” ;
- “zéro risque douane” ;
- “structure recommandée” sans nuance ;
- “micro-entreprise = piège” formulé comme règle générale absolue.

À préférer :
- “code HS indicatif à faire valider par transitaire/RDE” ;
- “checklist de conformité probable” ;
- “points d’attention réglementaires” ;
- “hypothèse de travail” ;
- “non destiné à remplacer une consultation juridique, fiscale, comptable ou douanière”.

---

## b) Exercice illégal d’une profession réglementée

La question contient quelques références imprécises : il n’existe pas, en tant que tel, un “Code de la sécurité financière” applicable ici. Les sujets pertinents sont plutôt les professions juridiques, comptables, douanières et éventuellement financières.

### Conseil juridique

La consultation juridique à titre habituel est encadrée.

Textes pertinents :
- **Loi n°71-1130 du 31 décembre 1971, art. 54** : seules certaines personnes peuvent donner des consultations juridiques ou rédiger des actes sous seing privé pour autrui à titre habituel et rémunéré.
- **Loi n°71-1130, art. 66-2** : sanction de l’exercice illégal.

Risque :
- faible si vous donnez de l’information générale ;
- moyen si vous proposez des choix personnalisés de structure ;
- élevé si vous rédigez statuts, contrats, consultations personnalisées, réponses individualisées juridiques/fiscales.

### Conseil fiscal / comptable

Textes pertinents :
- **Ordonnance n°45-2138 du 19 septembre 1945** sur l’ordre des experts-comptables.

Risque :
- faible si vous expliquez les mécanismes généraux ;
- moyen si vous recommandez un montage fiscal personnalisé ;
- élevé si vous tenez la comptabilité, préparez déclarations ou optimisez fiscalement un cas client.

### Douane / classement tarifaire / représentation

Le classement douanier, la déclaration et la représentation en douane sont très sensibles.

Textes pertinents :
- **Code des douanes de l’Union, art. 18** : représentation en douane.
- règles nationales sur les représentants en douane enregistrés.

Risque :
- faible si vous fournissez un code HS “indicatif” avec sources ;
- moyen si vous générez des codes HS personnalisés pour usage opérationnel ;
- élevé si vous présentez le code comme validé ou déposez/assistez directement à la déclaration douanière.

### Certifications CE/RoHS/REACH

Vous ne devez pas vous présenter comme organisme certificateur ou notifié.

Risque :
- faible si checklist ;
- moyen si “probablement conforme” ;
- élevé si “conforme CE validé”.

---

## c) Responsabilité si un client suit un agent et perd 50K€

Hypothèse : l’agent indique “code HS 7323.93, conforme”, le client importe, saisie douanière ou blocage, perte de 50K€.

Bases possibles de responsabilité :

### Responsabilité contractuelle

Si le client a payé un abonnement ou cours :
- **Code civil, art. 1231-1**.

Le client pourrait soutenir :
- mauvaise exécution du service ;
- information erronée ;
- manquement à une obligation de prudence ;
- défaut d’avertissement ;
- produit présenté comme plus fiable qu’il ne l’est.

### Responsabilité délictuelle

Pour un tiers ou hors contrat :
- **Code civil, art. 1240 et 1241**.

### Obligation d’information et pratiques trompeuses

Si la page de vente laisse croire que le système sécurise l’import :
- **Code conso, art. L111-1** ;
- **Code conso, art. L121-2 et L121-3**.

### Produit défectueux ?

Aujourd’hui, pour un pur contenu/logiciel d’aide à la décision, la responsabilité du fait des produits défectueux est moins évidente.  
Mais avec l’évolution européenne sur les logiciels et produits numériques, le risque va augmenter. En pratique, le risque principal reste contractuel/conso.

### Appréciation réaliste

Le disclaimer aide si :
- chaque sortie agent contient “indicatif / à valider” ;
- les sources sont visibles ;
- les incertitudes sont affichées ;
- le produit ne prétend pas remplacer un professionnel ;
- il existe des garde-fous pour les sujets critiques.

Il ne suffira pas si :
- le système donne des réponses impératives ;
- les pages marketing promettent “conformité” ou “sécurisation” ;
- aucune vérification humaine n’existe sur les drops payants ;
- les erreurs étaient prévisibles.

---

## d) Assurance RC professionnelle

Pas nécessairement obligatoire pour une activité SaaS/formation non réglementée.

Mais **fortement conseillée** avant facturation, surtout à 497 € / 1 497 € et abonnement.

À rechercher :
- RC professionnelle conseil/formation ;
- responsabilité médias / contenus ;
- erreurs et omissions ;
- cyber ;
- protection juridique ;
- couverture des dommages immatériels non consécutifs ;
- exclusion ou inclusion des outils IA.

**Risque sans assurance : MOYEN à ÉLEVÉ** dès que les utilisateurs prennent des décisions d’import à plusieurs milliers d’euros.

---

## e) CGV/CGU minimales avant de facturer

Avant toute vente, prévoir :

1. Identité complète du vendeur.
2. Description exacte du cours et du Roster.
3. Prix TTC, devise, modalités de paiement.
4. Accès, durée, modalités techniques.
5. Abonnement : reconduction, résiliation, préavis.
6. Droit de rétractation.
   - **Code conso, art. L221-18** : 14 jours.
   - Pour contenu numérique fourni immédiatement : consentement exprès à l’exécution immédiate et renonciation au droit de rétractation selon conditions applicables, notamment **Code conso, art. L221-28**.
7. Garantie légale de conformité des contenus/services numériques :
   - **Code conso, art. L224-25-1 et suivants**.
8. Limites d’usage : pas de conseil juridique/fiscal/douanier personnalisé.
9. Sorties IA : hypothèses, incertitudes, validation professionnelle obligatoire.
10. Propriété intellectuelle du cours et de la plateforme.
11. Interdiction de redistribution.
12. Responsabilité : obligation de moyens, pas de garantie de résultat.
13. Support et réclamations.
14. Médiation de la consommation :
   - **Code conso, art. L612-1**.
15. Données personnelles.
16. Droit applicable et juridiction, sans priver le consommateur de ses droits impératifs.

---

## Niveau de risque

### RISQUE MOYEN à ÉLEVÉ

- **Moyen** si le produit reste clairement pédagogique et indicatif.
- **Élevé** si les agents livrent des codes HS, certifications ou choix fiscaux comme recommandations opérationnelles fiables.

Probabilité réelle : **moyenne**, mais gravité forte en cas de perte client importante.

---

## Sanctions théoriques vs probables

Sanctions probables :
- demande de remboursement ;
- litige client ;
- signalement DGCCRF ;
- avis négatifs ;
- mise en cause responsabilité contractuelle ;
- demande d’indemnisation.

Sanctions plus graves :
- pratiques commerciales trompeuses ;
- exercice illégal si consultation juridique/fiscale personnalisée ;
- action civile en réparation.

---

## Correction concrète

Avant bêta payante :
- ajouter un bandeau de sortie agent : “indicatif — validation professionnelle requise” ;
- interdire dans le prompt agent les formulations “validé”, “conforme”, “garanti” ;
- classer les outputs par niveau de confiance ;
- imposer une “human review” pour tout drop monétisé ;
- ajouter CGV/CGU ;
- souscrire RC pro ;
- transformer les recommandations juridiques/fiscales en checklists de questions à poser à un professionnel.

---

# POINT 4 — PUBLICITÉ / MENTIONS LÉGALES / LCEN

## Diagnostic

La landing actuelle contient un footer, mais pas de vraies mentions légales.

Articles pertinents :
- **LCEN, loi n°2004-575 du 21 juin 2004, art. 6 III-1** : identification de l’éditeur.
- **LCEN, art. 6 III-2** : possibilité d’anonymat limitée pour non-professionnels, avec identification chez l’hébergeur.
- **LCEN, art. 20** : toute publicité accessible en ligne doit être clairement identifiable comme telle et rendre identifiable la personne pour le compte de laquelle elle est réalisée.
- **Code de la consommation, art. L121-1** : pratiques commerciales déloyales.
- **Code de la consommation, art. L121-2 et L121-3** : pratiques commerciales trompeuses.
- **Code de la consommation, art. L122-1 et suivants** : publicité comparative.
- **Loi n°2023-451 du 9 juin 2023** sur l’influence commerciale.

---

## a) Mentions légales obligatoires

Il manque :

Pour une personne morale :
- dénomination sociale ;
- forme sociale ;
- capital social ;
- adresse du siège ;
- numéro RCS/SIREN/SIRET ;
- numéro TVA intracommunautaire si applicable ;
- directeur de publication ;
- contact email/téléphone ;
- hébergeur : nom, dénomination, adresse, téléphone.

Pour une personne physique professionnelle :
- nom/prénom ;
- adresse professionnelle ;
- SIRET/RCS/RM si applicable ;
- email/contact ;
- directeur de publication ;
- hébergeur.

À ajouter aussi :
- politique de confidentialité ;
- CGV si vente ;
- CGU si accès plateforme ;
- médiateur consommation si vente B2C ;
- informations précontractuelles Code conso.

**Niveau de risque : MOYEN**  
En bêta fermée, risque DGCCRF faible. En lancement public payant, risque plus concret.

---

## b) Build in public / témoignages / preuve sociale

Points sensibles :

1. **Témoignages**
   - doivent être réels ;
   - datés ;
   - vérifiables ;
   - non sortis de leur contexte ;
   - autorisés par la personne.

2. **Compteurs**
   - “124 operators inscrits” doit être vrai ;
   - éviter les faux compteurs ou compteurs dynamiques inventés.

3. **Scarcity / urgence**
   - “bêta fermée”, “places limitées”, “drop incoming” doivent correspondre à une réalité.
   - Fausse rareté = pratique commerciale trompeuse.

4. **Comparaisons avec concurrents**
   La landing cite Steve Tan, Ecom King, etc.  
   La publicité comparative est autorisée si elle est :
   - objective ;
   - vérifiable ;
   - non trompeuse ;
   - non dénigrante ;
   - portant sur des biens/services répondant aux mêmes besoins.

Article pertinent :
- **Code conso, art. L122-1 et suivants**.

À corriger :
- “Steve Tan, Ecom King et les autres vendent…” : possible, mais attention au dénigrement.
- “promesses 8 figures en quelques jours” : à sourcer précisément ou reformuler.
- “nous avons une rigueur qu’ils n’ont pas” : risqué si non démontrable.

Préférer :
- “Contrairement à certaines formations du marché qui se concentrent sur l’apprentissage, le Roster fournit aussi des outils d’analyse semi-automatisée.”
- “Notre approche : coût complet, scénarios, validation professionnelle.”

---

## c) Clause d’insertion publicitaire / publicité identifiable

La “clause d’insertion publicitaire” renvoie ici à l’exigence de transparence publicitaire : ne pas dissimuler une communication commerciale.

Textes pertinents :
- **LCEN, art. 20** : publicité clairement identifiable.
- **Code conso, art. L121-2** : tromperie sur la nature commerciale.
- Loi influence commerciale 2023 : obligation d’indiquer clairement “Publicité” ou “Collaboration commerciale” pour les contenus d’influence.

Le projet n’a pas encore de témoignages ou avis “operators” visibles, mais il utilise :
- “Roster only” ;
- “operators” ;
- “manifest” ;
- “drop déclassifié” ;
- “fournisseur identifié”.

Ce vocabulaire est acceptable s’il ne crée pas une fausse impression :
- d’autorité officielle ;
- de certification ;
- de communauté massive inexistante ;
- de résultats déjà obtenus ;
- de disponibilité limitée fictive.

Interdits ou très risqués :
- avis inventés ;
- screenshots Slack/Discord fictifs ;
- faux revenus clients ;
- faux compteurs ;
- faux “bêta presque complète” ;
- témoignages IA non signalés ;
- affiliation non déclarée.

---

## Niveau de risque

### RISQUE MOYEN

Probabilité réelle :
- faible en bêta fermée ;
- moyenne en lancement public payant ;
- élevée si publicité comparative agressive ou témoignages non vérifiables.

---

## Sanctions théoriques vs probables

Sanctions théoriques :
- pratiques commerciales trompeuses : sanctions pénales et administratives.
- **Code conso, art. L132-2** : pratiques commerciales trompeuses punies notamment de 2 ans d’emprisonnement et 300 000 € d’amende, montant pouvant être porté proportionnellement aux avantages tirés.

Sanctions probables :
- signalement DGCCRF ;
- demande de modification ;
- bad buzz ;
- plainte concurrent ;
- litige client.

---

## Correction concrète

Avant bêta :
- ajouter vraies mentions légales ;
- supprimer ou sourcer les comparaisons nominatives agressives ;
- ne pas afficher de preuve sociale non vérifiée ;
- éviter tout faux compteur ;
- clarifier “bêta fermée” : nombre de places, critères, calendrier si utilisés ;
- afficher que les données produit sont indicatives et à valider.

---

## ⚖️ SOLUTION PRIORISÉE POUR LES TRANSCRIPTS (point 1)

| Solution | Risque résiduel | Effort | Recommandation |
|---|---:|---:|---|
| **Accord écrit avec chaque YouTubeur** couvrant reproduction, adaptation, synthèse, usage IA, cours, abonnement, durée, territoire, attribution | Faible | Élevé | Solution la plus sûre juridiquement. À viser pour lancement public. |
| **Supprimer les transcripts bruts et ne garder que des notes internes originales** sans verbatim, avec sources URL | Moyen à faible | Moyen | **Meilleure solution immédiate pour la bêta.** Réduit fortement le risque réel. |
| **Base de connaissance uniquement fondée sur faits, prix, ratios, checklists, méthodes générales**, sans structure ni formulations copiées | Moyen à faible | Moyen | À combiner avec suppression des transcripts. |
| **Attribution + citation stricte + courtes citations uniquement** | Moyen | Faible à moyen | Utile mais insuffisant si le système reste construit sur les transcripts. |
| **Reformulation totale des transcripts** | Moyen à élevé | Moyen | Insuffisant si la structure et la substance expressive restent reconnaissables. |
| **Vérifier les licences YouTube / Creative Commons** | Variable | Moyen | À faire vidéo par vidéo. Une licence CC peut aider mais ne couvre pas toujours tous les usages IA/commerciaux selon ses termes. |
| **Fair use américain** | Élevé | Faible | Inopérant comme stratégie en France. Ne pas s’appuyer dessus. |
| **Garder les transcripts bruts en interne “non affichés”** | Élevé | Faible | Risqué : reproduction et usage commercial indirect subsistent. |

### LA solution à appliquer en premier pour la bêta

**Supprimer les transcripts bruts du Roster et remplacer la base par des notes originales internes, non verbatim, sourcées par URL, avec citations très courtes uniquement si nécessaire.**

C’est le meilleur ratio réduction du risque / effort avant bêta.

---

## ✅ CHECKLIST CONFORMITÉ BÊTA FERMÉE (30-100 inscrits)

### Priorité 1 — avant ouverture bêta

- [ ] Geler l’usage des transcripts bruts YouTube dans le produit.
- [ ] Supprimer les `.txt` de l’environnement distribué, prod, démo, dépôt public.
- [ ] Reconstituer la knowledge base en notes internes originales.
- [ ] Supprimer tout passage verbatim non autorisé.
- [ ] Citer les sources uniquement sous forme bibliographique : titre, chaîne, URL, date.
- [ ] Ajouter une règle interne : aucune sortie agent ne doit reproduire un passage de transcript.
- [ ] Ajouter un disclaimer sur chaque drop : données indicatives, validation professionnelle requise.
- [ ] Interdire les formulations agent : “validé”, “conforme”, “garanti”, “zéro risque”.
- [ ] Mettre les codes HS en “indicatifs”.
- [ ] Mettre les certifications en “à vérifier / à faire valider”.

### Priorité 2 — socle légal site

- [ ] Ajouter mentions légales LCEN complètes.
- [ ] Ajouter politique de confidentialité séparée.
- [ ] Remplacer “Operator Roster” générique par vraie identité éditeur.
- [ ] Ajouter contact email effectif.
- [ ] Ajouter hébergeur.
- [ ] Supprimer le stockage email en `localStorage` ou le limiter strictement.
- [ ] Brancher la waitlist sur un prestataire email avec DPA.
- [ ] Conserver preuve du consentement : email, date, source, version de mention.
- [ ] Ajouter lien de désabonnement dans chaque email.
- [ ] Ne pas utiliser pixels publicitaires/analytics non essentiels sans consentement cookies.

### Priorité 3 — avant encaissement

- [ ] Rédiger CGV formation.
- [ ] Rédiger CGU Roster.
- [ ] Clarifier droit de rétractation / renonciation contenu numérique.
- [ ] Ajouter garantie légale de conformité numérique.
- [ ] Ajouter médiateur consommation.
- [ ] Ajouter politique de remboursement claire.
- [ ] Souscrire RC professionnelle adaptée.
- [ ] Prévoir validation humaine des drops envoyés aux clients.
- [ ] Reformuler les conseils structure juridique/fiscalité en informations générales.
- [ ] Supprimer les comparaisons concurrentes non sourcées ou agressives.

### Priorité 4 — propriété intellectuelle

- [ ] Lister les 7 chaînes utilisées.
- [ ] Identifier les vidéos réellement nécessaires.
- [ ] Vérifier licence de chaque vidéo.
- [ ] Préparer modèle d’autorisation/licence YouTubeur.
- [ ] Contacter les créateurs prioritaires avant usage public.
- [ ] Prévoir retrait rapide si un créateur s’oppose à l’usage.

---

## ⚠️ CHECKLIST CONFORMITÉ LANCEMENT PUBLIC (1000+ inscrits)

### Propriété intellectuelle

- [ ] Obtenir des accords écrits pour toute source YouTube substantiellement exploitée.
- [ ] Documenter les droits cédés : reproduction, adaptation, synthèse, IA, cours, abonnement, territoire, durée.
- [ ] Mettre en place registre des sources.
- [ ] Mettre en place procédure de retrait / notice-and-takedown interne.
- [ ] Auditer tous les contenus de cours pour éviter reprises non autorisées.
- [ ] Ne pas utiliser les noms de concurrents dans une publicité comparative non sourcée.

### RGPD / données personnelles

- [ ] Politique de confidentialité complète et versionnée.
- [ ] Registre des traitements RGPD.
- [ ] DPA signés avec tous les sous-traitants.
- [ ] Analyse des transferts hors UE.
- [ ] Process exercice droits RGPD sous 1 mois.
- [ ] Process suppression/désabonnement.
- [ ] Durée de conservation précise : par exemple jusqu’au désabonnement ou 3 ans d’inactivité.
- [ ] Sécurisation accès admin, MFA, limitation des droits.
- [ ] Plan de notification violation de données :
  - **RGPD, art. 33** : notification CNIL sous 72h si nécessaire.
  - **RGPD, art. 34** : information des personnes si risque élevé.
- [ ] Bandeau cookies si analytics/pixels non exemptés.
- [ ] Consentement spécifique pour prospection distincte si plusieurs finalités.

### E-commerce / consommation

- [ ] CGV complètes.
- [ ] CGU plateforme.
- [ ] Tunnel de commande conforme :
  - prix TTC ;
  - caractéristiques essentielles ;
  - durée engagement ;
  - reconduction ;
  - bouton de commande non ambigu.
- [ ] Gestion droit de rétractation conforme.
- [ ] Information sur garantie légale de conformité numérique.
- [ ] Médiateur consommation affiché.
- [ ] Facturation conforme.
- [ ] Conditions d’abonnement et résiliation simples.
- [ ] Process SAV/réclamation.

### Responsabilité / IA

- [ ] Validation humaine obligatoire des drops publics.
- [ ] Journalisation des sources et hypothèses utilisées par les agents.
- [ ] Score de confiance et limites affichées.
- [ ] Interdiction des affirmations réglementaires définitives.
- [ ] Clause claire : outil d’aide à la décision, pas conseil personnalisé.
- [ ] RC professionnelle active.
- [ ] Revue juridique des modules fiscalité/douane/conformité.
- [ ] Mise en place d’un process de correction rapide des erreurs.

### Publicité / acquisition

- [ ] Preuves sociales uniquement réelles et autorisées.
- [ ] Aucun faux compteur.
- [ ] Aucun faux témoignage.
- [ ] Aucun revenu client non vérifiable.
- [ ] Comparaisons concurrentes objectives et sourcées.
- [ ] Affiliations et partenariats clairement indiqués.
- [ ] Si influenceurs : mention “Publicité” ou “Collaboration commerciale” conforme à la loi 2023.
- [ ] Claims marketing relus sous l’angle **Code conso L121-2 / L121-3**.
- [ ] Éviter promesses de résultats financiers.

---

**Priorité réelle :** régler les transcripts avant tout. Le RGPD de la waitlist est corrigeable rapidement. Le vrai risque de blocage du projet vient de l’exploitation commerciale de contenus YouTube tiers et de la présentation des agents comme capables de sécuriser des décisions douanières/conformité.