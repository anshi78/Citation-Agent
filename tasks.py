import json
from pydantic import BaseModel
from typing import List

class Task(BaseModel):
    id: str
    difficulty: str
    claim: str
    ground_truth_title: str

TASKS = [
    Task(
        id="T001",
        difficulty="easy",
        claim="Search our database for the paper titled \"Acknowledgement to the Reviewers\". Submit its ID.",
        ground_truth_title="Acknowledgement to the Reviewers"
    ),
    Task(
        id="T002",
        difficulty="medium",
        claim="Find the paper \"Musing on Agri-History\". Verify its metadata and return its ID.",
        ground_truth_title="Musing on Agri-History"
    ),
    Task(
        id="T003",
        difficulty="hard",
        claim="Search the database for \"Instrumente und Methoden für das Kooperationsmanagement in Logistiknetzwerken\", check its citations, and submit its ID.",
        ground_truth_title="Instrumente und Methoden für das Kooperationsmanagement in Logistiknetzwerken"
    ),
    Task(
        id="T004",
        difficulty="easy",
        claim="Search our database for the paper titled \"Investigation of molecular mechanism of cardiomyocytes function at dilated cardiomyopathy using the model of mammals myocardium myofibrile reconstruction\". Submit its ID.",
        ground_truth_title="Investigation of molecular mechanism of cardiomyocytes function at dilated cardiomyopathy using the model of mammals myocardium myofibrile reconstruction"
    ),
    Task(
        id="T005",
        difficulty="medium",
        claim="Find the paper \"An Investigation into Blocking of Filial Imprinting in the Chick during Exposure to a Compound Stimulus\". Verify its metadata and return its ID.",
        ground_truth_title="An Investigation into Blocking of Filial Imprinting in the Chick during Exposure to a Compound Stimulus"
    ),
    Task(
        id="T006",
        difficulty="hard",
        claim="Search the database for \"Stability evaluation and enhancement methods in nanofluids: A review\", check its citations, and submit its ID.",
        ground_truth_title="Stability evaluation and enhancement methods in nanofluids: A review"
    ),
    Task(
        id="T007",
        difficulty="easy",
        claim="Search our database for the paper titled \"Abortion Rights Attitudes in Europe: Pro-Choice, Pro-Life, or Pro-Nation?\". Submit its ID.",
        ground_truth_title="Abortion Rights Attitudes in Europe: Pro-Choice, Pro-Life, or Pro-Nation?"
    ),
    Task(
        id="T008",
        difficulty="medium",
        claim="Find the paper \"Caracterização das estruturas de qualidade e segurança do doente\". Verify its metadata and return its ID.",
        ground_truth_title="Caracterização das estruturas de qualidade e segurança do doente"
    ),
    Task(
        id="T009",
        difficulty="hard",
        claim="Search the database for \"2C-17 花成誘導過程におけるLemna perpusilla 6746 の光感受性リズム再考\", check its citations, and submit its ID.",
        ground_truth_title="2C-17 花成誘導過程におけるLemna perpusilla 6746 の光感受性リズム再考"
    ),
    Task(
        id="T010",
        difficulty="easy",
        claim="Search our database for the paper titled \"Shortcomings of the bond orientational order parameters for the analysis of disordered particulate matter.\". Submit its ID.",
        ground_truth_title="Shortcomings of the bond orientational order parameters for the analysis of disordered particulate matter."
    ),
    Task(
        id="T011",
        difficulty="medium",
        claim="Find the paper \"線路部門 低速域における車輪/レールの粘着特性\". Verify its metadata and return its ID.",
        ground_truth_title="線路部門 低速域における車輪/レールの粘着特性"
    ),
    Task(
        id="T012",
        difficulty="hard",
        claim="Search the database for \"Prasa poznańska wobec zabójstwa prezydenta Narutowicza: opinie, argumenty, retoryka\", check its citations, and submit its ID.",
        ground_truth_title="Prasa poznańska wobec zabójstwa prezydenta Narutowicza: opinie, argumenty, retoryka"
    ),
    Task(
        id="T013",
        difficulty="easy",
        claim="Search our database for the paper titled \"Ecological Model Explaining the Psychosocial Adaptation to COVID-19\". Submit its ID.",
        ground_truth_title="Ecological Model Explaining the Psychosocial Adaptation to COVID-19"
    ),
    Task(
        id="T014",
        difficulty="medium",
        claim="Find the paper \"Protracted Adhesion of a Portion of the Placenta, with Final Sloughing and Separation\". Verify its metadata and return its ID.",
        ground_truth_title="Protracted Adhesion of a Portion of the Placenta, with Final Sloughing and Separation"
    ),
    Task(
        id="T015",
        difficulty="hard",
        claim="Search the database for \"Gratifikasi Generasi Millennial Membaca Line Today Dalam Media Sosial Line (Studi Kasus Terhadap Mahasiswa Dan Karyawan Swasta Sebagai Pengguna Line Today)\", check its citations, and submit its ID.",
        ground_truth_title="Gratifikasi Generasi Millennial Membaca Line Today Dalam Media Sosial Line (Studi Kasus Terhadap Mahasiswa Dan Karyawan Swasta Sebagai Pengguna Line Today)"
    ),
    Task(
        id="T016",
        difficulty="easy",
        claim="Search our database for the paper titled \"3D Topological Map Extraction From an Oriented Boundary Graph\". Submit its ID.",
        ground_truth_title="3D Topological Map Extraction From an Oriented Boundary Graph"
    ),
    Task(
        id="T017",
        difficulty="medium",
        claim="Find the paper \"Evaluation of the midwife led unit at the Royal Bournemouth Hospital\". Verify its metadata and return its ID.",
        ground_truth_title="Evaluation of the midwife led unit at the Royal Bournemouth Hospital"
    ),
    Task(
        id="T018",
        difficulty="hard",
        claim="Search the database for \"Interpretations of the Clean Water Act are as Muddy and Polluted as the Water the Act Seeks to Protect\", check its citations, and submit its ID.",
        ground_truth_title="Interpretations of the Clean Water Act are as Muddy and Polluted as the Water the Act Seeks to Protect"
    ),
    Task(
        id="T019",
        difficulty="easy",
        claim="Search our database for the paper titled \"11063 意匠設計における思考支援の研究 : ワイマール・バウハウス校長室のインテリア設計を例として\". Submit its ID.",
        ground_truth_title="11063 意匠設計における思考支援の研究 : ワイマール・バウハウス校長室のインテリア設計を例として"
    ),
    Task(
        id="T020",
        difficulty="medium",
        claim="Find the paper \"Immunoquantification and enzyme kinetics of alpha-L-iduronidase in cultured fibroblasts from normal controls and mucopolysaccharidosis type I patients.\". Verify its metadata and return its ID.",
        ground_truth_title="Immunoquantification and enzyme kinetics of alpha-L-iduronidase in cultured fibroblasts from normal controls and mucopolysaccharidosis type I patients."
    ),
    Task(
        id="T021",
        difficulty="hard",
        claim="Search the database for \"Flammability reduction of flexible polyurethane foams via carbon nanofiber network formation\", check its citations, and submit its ID.",
        ground_truth_title="Flammability reduction of flexible polyurethane foams via carbon nanofiber network formation"
    ),
    Task(
        id="T022",
        difficulty="easy",
        claim="Search our database for the paper titled \"Measurement of Cellular Immune Function of Breast Milk and Health Education of Pregnant and Lying in Women\". Submit its ID.",
        ground_truth_title="Measurement of Cellular Immune Function of Breast Milk and Health Education of Pregnant and Lying in Women"
    ),
    Task(
        id="T023",
        difficulty="medium",
        claim="Find the paper \"石窟庵 進入路邊의 朝鮮時代 磨崖碑\". Verify its metadata and return its ID.",
        ground_truth_title="石窟庵 進入路邊의 朝鮮時代 磨崖碑"
    ),
    Task(
        id="T024",
        difficulty="hard",
        claim="Search the database for \"Computational Intelligence in Astronomy - A Win-Win Situation\", check its citations, and submit its ID.",
        ground_truth_title="Computational Intelligence in Astronomy - A Win-Win Situation"
    ),
    Task(
        id="T025",
        difficulty="easy",
        claim="Search our database for the paper titled \"Synovial sarcoma of parapharyngeal and retropharyngeal space: A case report\". Submit its ID.",
        ground_truth_title="Synovial sarcoma of parapharyngeal and retropharyngeal space: A case report"
    ),
    Task(
        id="T026",
        difficulty="medium",
        claim="Find the paper \"MODULATION OF ENDOTHELIAL CELL ADHESION TO SYNTHETIC VASCULAR GRAFTS USING BIOTINYLATED FIBRONECTIN IN A DUAL LIGAND PROTEIN SYSTEM\". Verify its metadata and return its ID.",
        ground_truth_title="MODULATION OF ENDOTHELIAL CELL ADHESION TO SYNTHETIC VASCULAR GRAFTS USING BIOTINYLATED FIBRONECTIN IN A DUAL LIGAND PROTEIN SYSTEM"
    ),
    Task(
        id="T027",
        difficulty="hard",
        claim="Search the database for \"Locally Compact Groups and Haar Measure\", check its citations, and submit its ID.",
        ground_truth_title="Locally Compact Groups and Haar Measure"
    ),
    Task(
        id="T028",
        difficulty="easy",
        claim="Search our database for the paper titled \"[On Methodology of Developing Action Algorithm of Hygienic Processing of Hands And Application of Medical Gloves].\". Submit its ID.",
        ground_truth_title="[On Methodology of Developing Action Algorithm of Hygienic Processing of Hands And Application of Medical Gloves]."
    ),
    Task(
        id="T029",
        difficulty="medium",
        claim="Find the paper \"[Sterility in women and its relation to psychogenia. II].\". Verify its metadata and return its ID.",
        ground_truth_title="[Sterility in women and its relation to psychogenia. II]."
    ),
    Task(
        id="T030",
        difficulty="hard",
        claim="Search the database for \"Women and the politics of population and development in India\", check its citations, and submit its ID.",
        ground_truth_title="Women and the politics of population and development in India"
    ),
    Task(
        id="T031",
        difficulty="easy",
        claim="Search our database for the paper titled \"MATÉRIAU ACTIF D'ÉLECTRODE POSITIVE, ÉLECTRODE POSITIVE, BATTERIE, BLOC-BATTERIE, APPAREIL ÉLECTRONIQUE, VÉHICULE ÉLECTRIQUE, DISPOSITIF DE STOCKAGE D'ÉLECTRICITÉ ET SYSTÈME D'ALIMENTATION ÉLECTRIQUE\". Submit its ID.",
        ground_truth_title="MATÉRIAU ACTIF D'ÉLECTRODE POSITIVE, ÉLECTRODE POSITIVE, BATTERIE, BLOC-BATTERIE, APPAREIL ÉLECTRONIQUE, VÉHICULE ÉLECTRIQUE, DISPOSITIF DE STOCKAGE D'ÉLECTRICITÉ ET SYSTÈME D'ALIMENTATION ÉLECTRIQUE"
    ),
    Task(
        id="T032",
        difficulty="medium",
        claim="Find the paper \"Rookie rising.\". Verify its metadata and return its ID.",
        ground_truth_title="Rookie rising."
    ),
    Task(
        id="T033",
        difficulty="hard",
        claim="Search the database for \"Use of rotational transverse magnetometry to measure anisotropy energy\", check its citations, and submit its ID.",
        ground_truth_title="Use of rotational transverse magnetometry to measure anisotropy energy"
    ),
    Task(
        id="T034",
        difficulty="easy",
        claim="Search our database for the paper titled \"The Linkage Between Multiple Perspectives of the Marital Relationship and Preschoolers' Adjustment\". Submit its ID.",
        ground_truth_title="The Linkage Between Multiple Perspectives of the Marital Relationship and Preschoolers' Adjustment"
    ),
    Task(
        id="T035",
        difficulty="medium",
        claim="Find the paper \"Assessment of Peak Expiratory Flow Rate in Young Healthy Females Working In Clinical Laboratory in Air Conditioner\". Verify its metadata and return its ID.",
        ground_truth_title="Assessment of Peak Expiratory Flow Rate in Young Healthy Females Working In Clinical Laboratory in Air Conditioner"
    ),
    Task(
        id="T036",
        difficulty="hard",
        claim="Search the database for \"Chapter 2 From Real to Complex Analysis\", check its citations, and submit its ID.",
        ground_truth_title="Chapter 2 From Real to Complex Analysis"
    ),
    Task(
        id="T037",
        difficulty="easy",
        claim="Search our database for the paper titled \"22324 降伏機構を有するグルードインロッド接合の開発 : その3 T字型接合部試験(モーメント抵抗接合(2),構造III,2013年度日本建築学会大会(北海道)学術講演会・建築デザイン発表会)\". Submit its ID.",
        ground_truth_title="22324 降伏機構を有するグルードインロッド接合の開発 : その3 T字型接合部試験(モーメント抵抗接合(2),構造III,2013年度日本建築学会大会(北海道)学術講演会・建築デザイン発表会)"
    ),
    Task(
        id="T038",
        difficulty="medium",
        claim="Find the paper \"Domestic market as a development factor for Ukraine's metal industry\". Verify its metadata and return its ID.",
        ground_truth_title="Domestic market as a development factor for Ukraine's metal industry"
    ),
    Task(
        id="T039",
        difficulty="hard",
        claim="Search the database for \"Analiza naprężeń w warstwie wierzchniej szlifowanych ceramicznych części samochodowych za pomocą metody elementów skończonych\", check its citations, and submit its ID.",
        ground_truth_title="Analiza naprężeń w warstwie wierzchniej szlifowanych ceramicznych części samochodowych za pomocą metody elementów skończonych"
    ),
    Task(
        id="T040",
        difficulty="easy",
        claim="Search our database for the paper titled \"Zu Ch'ü Yüan's T'ien-Wen 天開: Ergänzungen und Berichtigungen zu Conrady-Erkes,Das älteste Dokument zur chinesischen Kunstgeschichte\". Submit its ID.",
        ground_truth_title="Zu Ch'ü Yüan's T'ien-Wen 天開: Ergänzungen und Berichtigungen zu Conrady-Erkes,Das älteste Dokument zur chinesischen Kunstgeschichte"
    ),
    Task(
        id="T041",
        difficulty="medium",
        claim="Find the paper \"Криминалистическое обеспечение расследования преступлений, совершенных организованными преступными группами в сфере экономики\". Verify its metadata and return its ID.",
        ground_truth_title="Криминалистическое обеспечение расследования преступлений, совершенных организованными преступными группами в сфере экономики"
    ),
    Task(
        id="T042",
        difficulty="hard",
        claim="Search the database for \"The Effect of Stimulus Salience on Over-selectivity\", check its citations, and submit its ID.",
        ground_truth_title="The Effect of Stimulus Salience on Over-selectivity"
    ),
    Task(
        id="T043",
        difficulty="easy",
        claim="Search our database for the paper titled \"Lannoo, Versele en Torck en geschiedkundige documentatie\". Submit its ID.",
        ground_truth_title="Lannoo, Versele en Torck en geschiedkundige documentatie"
    ),
    Task(
        id="T044",
        difficulty="medium",
        claim="Find the paper \"ON THE TAGGED RATIO METHODS TO REMOVE THE BIAS OF ESTIMATE CAUSED BY TYPE C SYSTEMATIC ERRORS IN THE PETERSEN-TYPE TAGGING EXPERIMENT\". Verify its metadata and return its ID.",
        ground_truth_title="ON THE TAGGED RATIO METHODS TO REMOVE THE BIAS OF ESTIMATE CAUSED BY TYPE C SYSTEMATIC ERRORS IN THE PETERSEN-TYPE TAGGING EXPERIMENT"
    ),
    Task(
        id="T045",
        difficulty="hard",
        claim="Search the database for \"Efficacy of recombinant subunit OMP and hly vaccines against Aeromonas hydrophila in Rohu (Labeo rohita).\", check its citations, and submit its ID.",
        ground_truth_title="Efficacy of recombinant subunit OMP and hly vaccines against Aeromonas hydrophila in Rohu (Labeo rohita)."
    ),
    Task(
        id="T046",
        difficulty="easy",
        claim="Search our database for the paper titled \"Traffic Arrows Increase Crew and Driver Safety\". Submit its ID.",
        ground_truth_title="Traffic Arrows Increase Crew and Driver Safety"
    ),
    Task(
        id="T047",
        difficulty="medium",
        claim="Find the paper \"Graphische Unterstützung der Informationssuche — Eine experimentelle Effizienzprüfung\". Verify its metadata and return its ID.",
        ground_truth_title="Graphische Unterstützung der Informationssuche — Eine experimentelle Effizienzprüfung"
    ),
    Task(
        id="T048",
        difficulty="hard",
        claim="Search the database for \"An ELM based Multi-Agent System and its applications to power generation\", check its citations, and submit its ID.",
        ground_truth_title="An ELM based Multi-Agent System and its applications to power generation"
    ),
    Task(
        id="T049",
        difficulty="easy",
        claim="Search our database for the paper titled \"Los servicios y las actividades culturales del Ayuntamiento de Madrid\". Submit its ID.",
        ground_truth_title="Los servicios y las actividades culturales del Ayuntamiento de Madrid"
    ),
    Task(
        id="T050",
        difficulty="medium",
        claim="Find the paper \"[Experimental study of instrumental dynamics applied to an automated endodontic system: the Canal Finder System (C.F.S.)].\". Verify its metadata and return its ID.",
        ground_truth_title="[Experimental study of instrumental dynamics applied to an automated endodontic system: the Canal Finder System (C.F.S.)]."
    ),
]

class Grader:
    def __init__(self, task: Task):
        self.task = task
        
    def score(self, submitted_paper_id: str, db_conn) -> float:
        cursor = db_conn.cursor()
        cursor.execute("SELECT title FROM s2_papers WHERE corpus_id = ? OR arxiv_id = ?", (submitted_paper_id, submitted_paper_id))
        res = cursor.fetchone()
        
        if not res:
            cursor.execute("SELECT title FROM arxiv_metadata WHERE arxiv_id = ?", (submitted_paper_id,))
            res = cursor.fetchone()
            
        if res and res[0].strip().lower() == self.task.ground_truth_title.strip().lower():
            return 1.0
        return 0.0
