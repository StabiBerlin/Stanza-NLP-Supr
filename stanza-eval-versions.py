import subprocess
import re
import os

def download_latest_eval_script():
    """Lädt die neueste Version von conll18_ud_eval.py herunter."""
    url = "https://universaldependencies.org/conll18/conll18_ud_eval.py"
    output_file = "conll18_ud_eval.py"
    
    if not os.path.exists(output_file):
        import urllib.request
        print("Lade neueste Version von conll18_ud_eval.py herunter...")
        urllib.request.urlretrieve(url, output_file)
        print("Download abgeschlossen!")
    else:
        print("Evaluationsskript bereits vorhanden.")

def run_evaluation(gold_file, system_file, output_file):
    """Führt die Evaluierung aus und speichert die Statistik in einer TXT-Datei."""
    try:
        process = subprocess.Popen(
            ["python", "conll18_ud_eval.py", gold_file, system_file, "--skip-token-check", "--verbose", "--counts"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if stderr:
            print("### Fehler während der Evaluation ###")
            print(stderr)
        
        sentence_stats = []
        overall_stats = {}

        for line in stdout.split("\n"):
            if "Metric" in line or "----" in line:
                continue  # Überspringe Tabellenkopf

            parts = [x.strip() for x in line.split("|") if x.strip()]
            if len(parts) == 5:
                metric, correct, gold_total, system_total, aligned = parts
                correct, gold_total, system_total, aligned = map(int, [correct, gold_total, system_total, aligned])
                sentence_stats.append({
                    "Metric": metric,
                    "Correct": correct,
                    "Gold Total": gold_total,
                    "System Total": system_total,
                    "Aligned": aligned
                })
                
                if metric not in overall_stats:
                    overall_stats[metric] = {"Correct": 0, "Gold Total": 0, "System Total": 0, "Aligned": 0}
                overall_stats[metric]["Correct"] += correct
                overall_stats[metric]["Gold Total"] += gold_total
                overall_stats[metric]["System Total"] += system_total
                overall_stats[metric]["Aligned"] += aligned

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("### Vereinheitlichte Evaluationsstatistik ###\n")
            f.write("Metric\tCorrect\tGold Total\tSystem Total\tAligned\tPrecision (%)\tRecall (%)\tF1-Score (%)\n")
            
            for stat in sentence_stats:
                metric = stat["Metric"]
                correct = stat["Correct"]
                gold_total = stat["Gold Total"]
                system_total = stat["System Total"]
                aligned = stat["Aligned"]

                precision = (correct / system_total) * 100 if system_total > 0 else 0
                recall = (correct / gold_total) * 100 if gold_total > 0 else 0
                f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                f.write(f"{metric}\t{correct}\t{gold_total}\t{system_total}\t{aligned}\t{precision:.2f}\t{recall:.2f}\t{f1_score:.2f}\n")

        print(f"Ergebnisse erfolgreich in {output_file} gespeichert.")

    except Exception as e:
        print(f"Fehler bei der Evaluierung: {e}")

def main():
    gold_file = "./out-chu-1.10.1/conllu/supr_all_segments.conllu"
    system_file = "./out-chu-1.9.0/conllu/supr_all_segments.conllu"  
    output_file = "evaluation_results.txt"
    
    download_latest_eval_script()
    print("Evaluierung nach Bereinigung der Tokenisierung:")
    run_evaluation(gold_file, system_file, output_file)

if __name__ == "__main__":
    main()

