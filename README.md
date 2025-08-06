# **Progetto "Schumi"**

Un sistema avanzato per la profilazione e il monitoraggio in tempo reale del conducente, progettato per aumentare la sicurezza e l'efficienza, e fornire assistenza alla guida personalizzata.

## **Descrizione**

**Schumi** è una piattaforma software che analizza il comportamento e lo stato dei conducenti attraverso un'architettura a due fasi. Prima, costruisce un profilo statico basato su un test attitudinale e sull'analisi dello stile di guida tramite Machine Learning in un ambiente simulato. Successivamente, monitora in tempo reale lo stato d'animo del conducente durante la guida effettiva, utilizzando la Computer Vision.

I dati raccolti vengono resi disponibili a servizi esterni per abilitare feedback, avvisi e raccomandazioni dinamiche e contestuali.

## **Caratteristiche Principali**

-   **Profilazione Multi-fattoriale:** Crea un profilo statico del conducente combinando i risultati di un test psicometrico con lo stile di guida rilevato tramite telemetria.
-   **Monitoraggio Real-Time:** Utilizza la Computer Vision per rilevare in tempo reale lo stato d'animo e il livello di attenzione (es. stanchezza, distrazione) del conducente.
-   **Architettura Disaccoppiata:** Sfrutta un broker MQTT per la comunicazione asincrona e API REST per l'esposizione sicura dei dati, garantendo flessibilità e scalabilità.
-   **Integrazione Esterna:** Fornisce dati completi a servizi di terze parti per abilitare un'assistenza alla guida realmente personalizzata.

## **Architettura in Breve**

Il sistema opera attraverso due macro-fasi distinte:

1.  **Fase 1: Profilazione Asincrona (Offline)**
    -   Il conducente compila un test attitudinale.
    -   I dati telemetrici vengono raccolti durante una sessione al simulatore (*Euro Truck Simulator 2*) e analizzati da un modello ML per definire lo stile di guida.
    -   I risultati vengono combinati e salvati come profilo statico nel database.

2.  **Fase 2: Monitoraggio Sincrono (Real-Time)**
    -   Durante la guida reale, una telecamera in cabina riprende il conducente.
    -   Un modello di Computer Vision analizza il flusso video per determinare lo stato d'animo e di attenzione in tempo reale.

## **Documentazione Completa**

Per una visione approfondita dell'architettura, dei diagrammi di flusso, dei requisiti tecnici e dello stato di avanzamento del progetto, si prega di consultare la documentazione completa sulla nostra pagina Notion.

**[➡️ Vai alla documentazione del progetto Schumi su Notion](https://lateral-saxophone-9f2.notion.site/Schumi-239521f00178802799d8c87bbae81bf7)**
