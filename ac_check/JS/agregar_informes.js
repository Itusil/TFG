
main();

/**
 * Loads the content of the stored JSON in each table
 * If there is no stored JSON, it will display a message saying that there is no data saved.
 * */
function main(){
    var jsonT = localStorage.getItem("json");
    var jsonTabla = localStorage.getItem("tabla_resultados");
    var json = JSON.parse(jsonT);
    var texto = "";

    if (json == null){
        texto = "<div style='text-align:center'><text style='font-size:14px'>No data stored</text></div>";
    }else{
        texto = jsonTabla;
    }

    var loc = window.location.hostname;

    var main = localStorage.getItem("tabla_main");
    var texto2 = "";

    if (main == null){
        texto2 = "<text style='font-size:26px'></text>";
    }else{
        texto2 = main;
    }
    if(loc !== 'www.w3.org'){
        document.getElementById("tabla_res").innerHTML = texto;
        document.getElementById('tabla_contenido').innerHTML=texto2;
    }
}

/**
 * Merge the two JSON passed by parameters to get a single JSON
 * 
 * The result is stored in the first parameter
 * 
 * */
function merge(json,json1){
    //First we check if the conditions for the merge are met:
    //They both have to be AA:
    var tipo_1 = json.defineScope.conformanceTarget;
    var tipo_2 = json1.defineScope.conformanceTarget;

    if(tipo_1 !=="AA" || tipo_2 !== "AA"){
        alert("Aggregation not possible, both files must have a conformance target of AA.");
        return;
    }
    if(json.defineScope.scope.title !== json1.defineScope.scope.title){
        alert("Aggregation not possible, the website names of the files doesn't match.");
        return; 
    }

    merge_reportFindings(json,json1);
    merge_audit_samples(json,json1);
}

/**
 * Returns a JSON with the W3C web format completely cleaned of data.
 * */
function crear_JSON_limpio(){
    var json = {"@context":{"reporter":"http://github.com/w3c/wai-wcag-em-report-tool/","wcagem":"http://www.w3.org/TR/WCAG-EM/#","Evaluation":"wcagem:procedure","defineScope":"wcagem:step1","scope":"wcagem:step1a","step1b":{"@id":"wcagem:step1b","@type":"@id"},"conformanceTarget":"step1b","accessibilitySupportBaseline":"wcagem:step1c","additionalEvaluationRequirements":"wcagem:step1d","exploreTarget":"wcagem:step2","essentialFunctionality":"wcagem:step2b","pageTypeVariety":"wcagem:step2c","technologiesReliedUpon":"wcagem:step2d","selectSample":"wcagem:step3","structuredSample":"wcagem:step3a","randomSample":"wcagem:step3b","Website":"wcagem:website","Webpage":"wcagem:webpage","auditSample":"wcagem:step4","reportFindings":"wcagem:step5","documentSteps":"wcagem:step5a","commissioner":"wcagem:commissioner","evaluator":"wcagem:evaluator","evaluationSpecifics":"wcagem:step5b","WCAG":"http://www.w3.org/TR/WCAG/#","WCAG20":"http://www.w3.org/TR/WCAG20/#","WCAG21":"http://www.w3.org/TR/WCAG21/#","WAI":"http://www.w3.org/WAI/","A":"WAI:WCAG2A-Conformance","AA":"WAI:WCAG2AA-Conformance","AAA":"WAI:WCAG2AAA-Conformance","wcagVersion":"WAI:standards-guidelines/wcag/#versions","reportToolVersion":"wcagem:reportToolVersion","earl":"http://www.w3.org/ns/earl#","Assertion":"earl:Assertion","TestMode":"earl:TestMode","TestCriterion":"earl:TestCriterion","TestCase":"earl:TestCase","TestRequirement":"earl:TestRequirement","TestSubject":"earl:TestSubject","TestResult":"earl:TestResult","OutcomeValue":"earl:OutcomeValue","Pass":"earl:Pass","Fail":"earl:Fail","CannotTell":"earl:CannotTell","NotApplicable":"earl:NotApplicable","NotTested":"earl:NotTested","assertedBy":"earl:assertedBy","mode":"earl:mode","result":"earl:result","subject":"earl:subject","test":"earl:test","outcome":"earl:outcome","dcterms":"http://purl.org/dc/terms/","title":"dcterms:title","description":"dcterms:description","summary":"dcterms:summary","date":"dcterms:date","hasPart":"dcterms:hasPart","isPartOf":"dcterms:isPartOf","id":"@id","type":"@type","language":"@language"},"language":"en","type":"Evaluation","reportToolVersion":"3.0.3","defineScope":{"id":"_:defineScope","scope":{"description":"","title":""},"conformanceTarget":"AA","accessibilitySupportBaseline":"","additionalEvaluationRequirements":"","wcagVersion":"2.1"},"exploreTarget":{"id":"_:exploreTarget","essentialFunctionality":"","pageTypeVariety":"","technologiesReliedUpon":[]},"selectSample":{"id":"_:selectSample","structuredSample":[],"randomSample":[]},"auditSample":[{"type":"Assertion","date":"2022-03-01T18:51:57.699Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.699Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:non-text-content","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.700Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.700Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:audio-only-and-video-only-prerecorded","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.700Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.700Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:captions-prerecorded","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.700Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.700Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:audio-description-or-media-alternative-prerecorded","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:captions-live","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:audio-description-prerecorded","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:info-and-relationships","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:meaningful-sequence","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:sensory-characteristics","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.701Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:orientation","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.701Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:identify-input-purpose","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:use-of-color","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:audio-control","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:contrast-minimum","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:resize-text","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:images-of-text","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.540Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:reflow","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:non-text-contrast","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:text-spacing","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:content-on-hover-or-focus","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:keyboard","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:no-keyboard-trap","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:character-key-shortcuts","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.702Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:timing-adjustable","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.702Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:pause-stop-hide","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:three-flashes-or-below-threshold","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:bypass-blocks","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:page-titled","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:focus-order","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:link-purpose-in-context","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:multiple-ways","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:headings-and-labels","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:focus-visible","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:pointer-gestures","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:pointer-cancellation","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:label-in-name","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.703Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.703Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:motion-actuation","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:language-of-page","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:language-of-parts","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:on-focus","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:on-input","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:consistent-navigation","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:consistent-identification","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.541Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:error-identification","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:labels-or-instructions","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:error-suggestion","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:error-prevention-legal-financial-data","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.704Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.704Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:parsing","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.705Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.705Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:name-role-value","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}},{"type":"Assertion","date":"2022-03-01T18:51:57.705Z","mode":{"type":"TestMode","@value":"earl:manual"},"result":{"type":"TestResult","date":"2022-03-01T18:51:57.705Z","description":"","outcome":{"id":"earl:untested","type":["OutcomeValue","NotTested"]}},"subject":{"id":"_:subject_1","type":["TestSubject","Website"],"date":"2022-03-01T18:51:52.539Z","description":"","title":""},"test":{"id":"WCAG21:status-messages","type":["TestCriterion","TestRequirement"],"date":"2022-03-01T18:51:52.542Z"}}],"reportFindings":{"date":{"type":"http://www.w3.org/TR/NOTE-datetime","@value":"Tue Mar 01 1999"},"summary":"","title":"","commissioner":"","evaluator":"","documentSteps":[{"id":"_:about"},{"id":"_:defineScope"},{"id":"_:exploreTarget"},{"id":"_:selectSample"}],"evaluationSpecifics":""}};
    return json;
}

/**
 * Merges the results of the second JSON given by parameter with the first one
 * */
function merge_reportFindings(json, json1){
    //Date
    let fecha = Date.parse(json.reportFindings.date["@value"]);
    let fecha1 = Date.parse(json1.reportFindings.date["@value"]);
    
    //The most recent date is written
    if(fecha < fecha1){
        json.reportFindings.date["@value"] = json1.reportFindings.date["@value"];
    }

    //Evaluator: The creator, if it is empty, set the creator of the imported document, otherwise leave the original.
    if(json.reportFindings.evaluator == ""){
        json.reportFindings.evaluator = json1.reportFindings.evaluator;
    }

    //Commissioner: Who has done it, they are added
    let commissioner = json.reportFindings.commissioner;
    let commissioner1 =  json1.reportFindings.commissioner;
    if(commissioner !== ""){
        json.reportFindings.commissioner= commissioner+" & "+commissioner1;
    }else if(commissioner1 !== ""){
        json.reportFindings.commissioner= commissioner1;
    }


    //Summary
    let summary = json.reportFindings.summary;
    let summary1 = json1.reportFindings.summary;
    console.log("1: "+summary+" 2: "+summary1);

    if(summary == ""){
        json.reportFindings.summary= summary1;
    }else if(summary1 !== ""){
        json.reportFindings.summary= summary+" & "+summary1;
    }


    //Evaluation specifics
    /*
    WCAG-EM suggests that you archive the web pages audited. For more information, see WCAG-EM Step 5.b: Record the Evaluation
     Specifics. You can use this text field to record the evaluation tools, web browsers, assistive technologies, 
     other software, and methods used for the evaluation. What you enter here will be included in the generated report. 
     After you download the report, you could delete or edit this information in the HTML file before submitting the report.
    */
    let evaluationSpecifics = json.reportFindings.evaluationSpecifics;
    let evaluationSpecifics1 =  json1.reportFindings.evaluationSpecifics;
    if(evaluationSpecifics !== ""){
        json.reportFindings.evaluationSpecifics= evaluationSpecifics+" & "+evaluationSpecifics1;
    }else if(evaluationSpecifics1 !== ""){
        json.reportFindings.evaluationSpecifics= evaluationSpecifics1;
    }

    return json;
}


/**
 * Download the text passed as a parameter ("text") into a document named "filename".
 * */
function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

/**
 * Merges the tests of the two JSON passed by parameter and saves them in "primario".
 * 
 * The length of both JSON must be the same, because they will both be conformance target: 'AA'.
 * */
function merge_audit_samples(primario,secundario){
    var arr_sec = secundario.auditSample;
    let longitud = primario.auditSample.length;

    let texto = "";
    var obj_prim;

    var res_prov1;
    var res_prov2;        
    var au1 = {};
    var au2 = {};
    var codigos1;
    var codigos2;

    var com1 = primario.reportFindings.evaluator;
    var com2 = secundario.reportFindings.evaluator;

    var au1_des = "";
    var au2_des = "";


    for (var i = 0; i <longitud; i++){
        texto = "";
        obj_prim = primario.auditSample[i];
        //console.log(obj_prim.test.id);

        /*
        --------------------Criteria---------------------
        -If one of the two is "failed", result is "failed".
        -If one is "untested" and the other is tested, the result of the other is set.
        -If one is "cantTell" and the other has a result, the result of the other is set.
        */

        //We check if it happens in the original.
        res_prov1 = primario.auditSample[i].result.outcome.id;
        res_prov2 = secundario.auditSample[i].result.outcome.id;

        au1 = primario.auditSample[i];
        au2 = secundario.auditSample[i];

        au1_des = primario.auditSample[i].result.description;
        au2_des = secundario.auditSample[i].result.description;

        codigos1 = primario.auditSample[i].result.codigo_error;
        codigos2 = secundario.auditSample[i].result.codigo_error;


        switch(true){

            //Case the first one untested and the second one not untested
            case(res_prov1 == "earl:untested" && res_prov2 !== "earl:untested"):

                primario.auditSample[i].result = au2.result;
                break;

            //Case both fail: Descriptions are added together
            case(res_prov1 == "earl:failed" && res_prov2 == "earl:failed"):
                break;
            //Case the second is failed, it doesn't matter what is first.
            case(res_prov2 == "earl:failed"):
                primario.auditSample[i].result= au2.result;
                break;

            //Case the first is cantTell and the second is different from cantTell
            case(res_prov1 == "earl:cantTell" && res_prov2 !== "earl:cantTell"):
                primario.auditSample[i].result = au1.result;
                break;
            default:
                break;
        }
        if(!au1_des.startsWith('<b>@') && au1_des !== ''){
            primario.auditSample[i].result.description="<b>@"+com1+'</b>['+res_prov1.substring(5)+']: '+au1_des;
        }else{
            primario.auditSample[i].result.description=au1_des;
        }
        if(au2_des !== ''){
            if(primario.auditSample[i].result.description !== ''){
                primario.auditSample[i].result.description+="<br><br>";
            }
            primario.auditSample[i].result.description+="<b>@"+com2+'</b>['+res_prov2.substring(5)+']: '+au2_des;
        }


        //We add codes which the user will be able to click on to find them
        if(codigos1 !== undefined && codigos2 !== undefined){
            //Setting the codes
            switch(true){
                //Case one empty and the other full
                case (codigos1.length === 0 && codigos2.length !==0):
                    primario.auditSample[i].result.codigo_error = codigos2;
                    break;
                //Case one empty and the other full
                case (codigos1.length !== 0 && codigos2.length ===0):
                    primario.auditSample[i].result.codigo_error = codigos1;
                    break;
                //Case both full, concatenate the arrays
                case (codigos1.length !== 0 && codigos2.length !==0):
                    let array_merged = codigos1.concat(codigos2);
                    primario.auditSample[i].result.codigo_error = array_merged;
                    break;
                //Remaining case: Both emtpy
                default:
                    primario.auditSample[i].result.codigo_error = [];
            }
        //If it reaches the "else", it means that one of the two has no code. The code of the one that has the code is put in.
        }else{
            if(codigos1 !== undefined){
                primario.auditSample[i].result.codigo_error = codigos1;
            }
            if(codigos2 !== undefined){
                primario.auditSample[i].result.codigo_error = codigos2;     
            }
        }
    }
}
