import csv
import io
from datetime import datetime, date
from app.utils.supabase_client import get_supabase_admin


def get_report():
    supabase = get_supabase_admin()
    now = date.today()

    # 1. Candidatos activos
    candidates = supabase.table("candidates") \
        .select("id, name, party, photo_url") \
        .eq("is_active", True) \
        .execute().data

    # 2. Todas las votes (solo candidate_id)
    all_votes = supabase.table("votes") \
        .select("candidate_id") \
        .execute().data

    total_votes = len(all_votes)

    # 3. Resultados por candidato
    results = []
    for c in candidates:
        cid = c["id"]
        count = sum(1 for v in all_votes if v["candidate_id"] == cid)
        results.append({
            "candidate_id": cid,
            "name": c["name"],
            "party": c["party"],
            "photo_url": c.get("photo_url"),
            "total": count,
            "percentage": round((count / total_votes * 100), 2) if total_votes else 0.0
        })

    # 4. Votos en blanco
    blank_votes = sum(1 for v in all_votes if v["candidate_id"] is None)
    blank_percentage = round((blank_votes / total_votes * 100), 2) if total_votes else 0.0

    # 5. Votantes totales (registro completado)
    total_voters = supabase.table("voters") \
        .select("id", count="exact") \
        .execute()
    total_voters_count = total_voters.count or 0

    # 6. Turnout por edad
    turnout_by_age = {"18-25": 0, "26-40": 0, "41-60": 0, "60+": 0}
    voted_by_age = {"18-25": 0, "26-40": 0, "41-60": 0, "60+": 0}

    all_voters = supabase.table("voters") \
        .select("id, birth_date") \
        .execute().data

    voted_ids = supabase.table("vote_tokens") \
        .select("voter_id") \
        .execute().data
    voted_set = {v["voter_id"] for v in voted_ids}

    def age_from_birth(birth_str):
        if not birth_str:
            return None
        b = datetime.strptime(birth_str[:10], "%Y-%m-%d").date()
        return now.year - b.year - ((now.month, now.day) < (b.month, b.day))

    for voter in all_voters:
        age = age_from_birth(voter.get("birth_date"))
        if age is None:
            continue
        if age <= 25:
            bucket = "18-25"
        elif age <= 40:
            bucket = "26-40"
        elif age <= 60:
            bucket = "41-60"
        else:
            bucket = "60+"
        turnout_by_age[bucket] = turnout_by_age.get(bucket, 0) + 1
        if voter["id"] in voted_set:
            voted_by_age[bucket] = voted_by_age.get(bucket, 0) + 1

    age_report = {}
    for bucket in ["18-25", "26-40", "41-60", "60+"]:
        total = turnout_by_age[bucket]
        voted = voted_by_age[bucket]
        age_report[bucket] = {
            "total": total,
            "voted": voted,
            "percentage": round((voted / total * 100), 2) if total else 0.0
        }

    return {
        "results": sorted(results, key=lambda x: x["total"], reverse=True),
        "blank_votes": {"total": blank_votes, "percentage": blank_percentage},
        "total_voters": total_voters_count,
        "total_votes": total_votes,
        "turnout_percentage": round((total_votes / total_voters_count * 100), 2) if total_voters_count else 0.0,
        "turnout_by_age": age_report
    }


def get_report_csv():
    data = get_report()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Resultados por candidato"])
    writer.writerow(["Candidato", "Partido", "Votos", "Porcentaje"])
    for r in data["results"]:
        writer.writerow([r["name"], r["party"], r["total"], f"{r['percentage']}%"])
    writer.writerow([])

    writer.writerow(["Votos en blanco", data["blank_votes"]["total"], f"{data['blank_votes']['percentage']}%"])
    writer.writerow([])

    writer.writerow(["Totales"])
    writer.writerow(["Votantes registrados", data["total_voters"]])
    writer.writerow(["Votos emitidos", data["total_votes"]])
    writer.writerow(["Participación", f"{data['turnout_percentage']}%"])
    writer.writerow([])

    writer.writerow(["Participación por edad"])
    writer.writerow(["Rango", "Total", "Votaron", "%"])
    for bucket, info in data["turnout_by_age"].items():
        writer.writerow([bucket, info["total"], info["voted"], f"{info['percentage']}%"])

    return output.getvalue()