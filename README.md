## queries
- given a tax code it returns when the last certificate expires.
- given the UCI of green pass returns the expiration date.
- return all the certificates generated by an invalid sanitary operator performance in a certain date
- return the doctor that failed an anamnesi
- return all the historic(all vaccines and tests) of a given person

## commands
- add a vaccination to a given person
- change the expiration date of a specific type of certificate (f.i: government rules changed and from now certificates released after
the second dose of a specific brand will last 12 month instead of 6(?)).
- (?)


## hypothesis 
recovery motivation: bisogna distinguere i tamponi con esito negativo come semplice controllo da quelli effettuati dopo
un'infezione. Utilizzare il documento recovery può essere di aiuto per dover evitare di fare il controllo sulle sequenze 
di tamponi e sulle date. Il recovery certificate non viene rilasciato in maniera automatica dopo la guarigione, ma viene 
caricato manualmente da chi di competenza dopo un iter specifico.
Il recovery certificate non è richiesto da specifica ma può essere usato come supporto per poter calcolare la data di 
scadenza del certificato.


Per far riferimento ad un authorized body nel documento Place si è pensato di utilizzare un pointer a differenza di un sottodocumento,
in quanto gli enti sono pochi e vengono ripetuti molte volte. Sebbene in MongoDB le ridondanze non siano gravi, riteniamo che questo tipo di informazione 
raramente possa tornare utile, per questo motivo si è pensato che la replica di tali dati sia eccessiva.


Per semplificare le query per quanto riguarda la validità di un documento, possiamo assumere che per il db sia usato in uno 
specifico stato (italia) e quindi la legge è unica e che per ogni tipo di certificato, l'intervallo di validità è noto e ben definito.
In questo modo possiamo mettere la data di scadenza di un certificato nel db. L'utilità sta nel fatto che nella query non c'è bisogno di calcolare 
la data di scadenza controllando il tipo di certificato. Per esempio: se volessi vedere fino a quando sono in regola dovrei creare una query che per ogni tipo
di certificato mi calcola in maniera diversa la data di scadenza, nel metodo proposto non dobbiamo preoccuarci di fare ciò perchè è già tutto calcolato.
Questo ci permette di aggiungere tra i comandi la possibilità di cambiare le date di scadenza di un determinato tipo di certificato. L'operazione potrebbe essere
onerosa ma sarebbe comunque molto rara, quindi è un costo che possiamo permetterci.


da specifica una persona corrisponde 1 a 1 con il certificato che corrisponde a tutto lo storico. Noi vogliamo creare il db che contiene 
certificati come green pass. Se facciamo cosi dobbiamo scrivere il perchè della scelta:
 - da specifica bisogna supportare un'applicazione per verificare la validità di un certificato (green pass) la verfica averrà verificando l'UCI del certificato
 e non attraverso il nome e cognome. Creare un grosso documento per ogni persona non è efficiente come tenere direttamente tutti i documenti separati, infatti il db può essere
 indicizzato per UCI, invece usando l'alternativa dei document grossi bisognerebbe indicizzare le persone per nome e cognome e bisognerebbe controllare per ogni persona se 
 possiede un certificato identificato dall'UCI dato.
 - il db dovrebbe poter essere utilizzato anche per poter visualizzare l'intero storico covid di una determinata persona. Assumendo che una persona possa essere identificata
 attraverso il codice fiscale (NB: nel qr code non esiste questa informazione, quindi per il punto precedente questa considerazione non è applicabile), basta indicizzare i   documenti per codice fiscale, in questo modo il filtraggio per codice fiscale è rapido in ogni caso. Da questo punto in poi tutto ciò che si può fare nel modello proposto da specifica può essere fatto allo stesso modo con il modello proposto da noi. (in realtà dobbiamo verificare che le query siano effettivamente semplici, ma così dovrebbe essere).
 
NB: sappiamo che in questo modo c'è ridondanza dei dati per quanto riguarda l'anagrafica degli utenti ma è qualcosa che possiamo permetterci data la finalità di mongoDB
