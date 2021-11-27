## queries
- given a tax code it returns the last released certificate for each type
- given data from qr code(name, surname, dob and uci), returns the release data of the certificate (
the type field should be considered, so that it can be returned, and the expiration date can be correctly calculated. 
). **Another consideration about the query**: should we search by tax code or by personal data (name, surname, dob)?
  The second one sounds better as qr codes embed only these data.
- return all the certificates generated by an invalid sanitary operator performance in a certain date
- return the doctor that failed an anamnesi
- (?) find all vaccines and tests performed in a certain facility. we are not sure this is a good query for our db purposes.
- return the result of the last swab  

## commands
add vaccination for a recovered person 


## hypothesis 
recovery motivation: bisogna distinguere i tamponi con esito negativo come semplice controllo da quelli effettuati dopo
un'infezione. Utilizzare il documento recovery può essere di aiuto per dover evitare di fare il controllo sulle sequenze 
di tamponi e sulle date. Il recovery certificate non viene rilasciato in maniera automatica dopo la guarigione, ma viene 
caricato manualmente da chi di competenza dopo un iter specifico.
Il recovery certificate non è richiesto da specifica ma può essere usato come supporto per poter calcolare la data di 
scadenza del certificato.