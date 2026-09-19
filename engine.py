from fractions import Fraction

# =========================
# ISLAMIC FIQH ENGINE
# =========================

class Engine:
    def __init__(self, estate):
        self.estate = Fraction(estate)
        self.heirs = {}

    def add(self, name, count):
        if count > 0:
            self.heirs[name] = count

    def calc(self):
        shares = {}
        h = self.heirs
        
        # Retrieve heir counts
        sons = h.get("son", 0)
        daughters = h.get("daughter", 0)
        father = h.get("father", 0)
        mother = h.get("mother", 0)
        husbands = h.get("husband", 0)
        wives = h.get("wife", 0)
        
        pat_gf = h.get("paternal_grandfather", 0)
        mat_gf = h.get("maternal_grandfather", 0)
        pat_gm = h.get("paternal_grandmother", 0)
        mat_gm = h.get("maternal_grandmother", 0)
        
        bros = h.get("brother", 0)
        siss = h.get("sister", 0)
        pat_bros = h.get("paternal_brother", 0)
        pat_siss = h.get("paternal_sister", 0)
        mat_bros = h.get("maternal_brother", 0)
        mat_siss = h.get("maternal_sister", 0)
        
        pat_uncle = h.get("paternal_uncle", 0)
        mat_uncle = h.get("maternal_uncle", 0)

        # Fiqh Conditions
        children_exist = (sons + daughters) > 0
        male_descendants = sons > 0
        sibling_count = bros + siss + pat_bros + pat_siss + mat_bros + mat_siss
        siblings_exist = sibling_count >= 2

        total_fixed = Fraction(0)

        # --- 1. FIXED SHARES (Ashab al-Furud) ---
        
        # Spouses
        if husbands > 0:
            share = Fraction(1, 4) if children_exist else Fraction(1, 2)
            shares["husband"] = share
            total_fixed += share
        elif wives > 0:
            share = Fraction(1, 8) if children_exist else Fraction(1, 4)
            shares["wife"] = share
            total_fixed += share

        # Mother & Grandmothers
        if mother > 0:
            share = Fraction(1, 6) if (children_exist or siblings_exist) else Fraction(1, 3)
            # Umariyyatain simplified: Mother takes 1/3 of remainder if only parents and spouse survive
            if not children_exist and sibling_count == 0 and father > 0 and pat_gf == 0:
                spouse_share = shares.get("husband", Fraction(0)) + shares.get("wife", Fraction(0))
                share = Fraction(1, 3) * (Fraction(1) - spouse_share)
            shares["mother"] = share
            total_fixed += share
        else:
            gm_count = 0
            if mat_gm > 0: gm_count += 1
            if pat_gm > 0 and father == 0: gm_count += 1
            if gm_count > 0:
                shares["grandmothers_shared"] = Fraction(1, 6)
                total_fixed += shares["grandmothers_shared"]

        # Father & Paternal Grandfather
        if father > 0:
            if male_descendants:
                share = Fraction(1, 6)
                shares["father"] = share
                total_fixed += share
            elif daughters > 0:
                share = Fraction(1, 6) # Gets 1/6 + Asaba later
                shares["father"] = share
                total_fixed += share
        elif pat_gf > 0:
            if male_descendants:
                share = Fraction(1, 6)
                shares["paternal_grandfather"] = share
                total_fixed += share
            elif daughters > 0:
                share = Fraction(1, 6)
                shares["paternal_grandfather"] = share
                total_fixed += share

        # Daughters (if no sons)
        if daughters > 0 and sons == 0:
            share = Fraction(1, 2) if daughters == 1 else Fraction(2, 3)
            shares["daughter"] = share
            total_fixed += share

        # Full Sisters (Fixed share if no sons, daughters, father, pat_gf, or full brothers)
        if daughters == 0 and sons == 0 and father == 0 and pat_gf == 0 and bros == 0:
            if siss > 0:
                share = Fraction(1, 2) if siss == 1 else Fraction(2, 3)
                shares["sister"] = share
                total_fixed += share
                
        # Paternal Sisters (Fixed share)
        if daughters == 0 and sons == 0 and father == 0 and pat_gf == 0 and pat_bros == 0 and bros == 0:
            if siss == 0:
                if pat_siss > 0:
                    share = Fraction(1, 2) if pat_siss == 1 else Fraction(2, 3)
                    shares["paternal_sister"] = share
                    total_fixed += share
            elif siss == 1:
                if pat_siss > 0:
                    share = Fraction(1, 6) # Completes the 2/3 maximum limit for females
                    shares["paternal_sister"] = share
                    total_fixed += share

        # Maternal Siblings (Blocked by children, father, and true grandfather)
        mat_total = mat_bros + mat_siss
        if not children_exist and father == 0 and pat_gf == 0:
            if mat_total > 0:
                share = Fraction(1, 6) if mat_total == 1 else Fraction(1, 3)
                shares["maternal_siblings"] = share
                total_fixed += share

        # --- AL-MUSHTARAKAH (Himariyya / Donkey Case) FIX ---
        # Triggered when Husband (1/2) + Mother/Grandmother (1/6) + Mat Sibs (1/3) exhaust the 1.0 estate, leaving 0 for Full brothers.
        is_mushtarakah = False
        if husbands == 1 and not children_exist and father == 0 and pat_gf == 0:
            if mat_total >= 2 and bros > 0:
                if mother > 0 or ("grandmothers_shared" in shares):
                    is_mushtarakah = True
                    
                    # Convert Maternal Siblings Fixed Share into a Pool Shared equally by Maternal & Full Siblings
                    total_fixed -= shares["maternal_siblings"]
                    del shares["maternal_siblings"]
                    
                    shares["mushtarakah_pool"] = Fraction(1, 3)
                    total_fixed += shares["mushtarakah_pool"]

        # --- 2. 'AWL (Oversubscription Reduction) ---
        if total_fixed > 1:
            for k in shares:
                shares[k] = shares[k] / total_fixed
            total_fixed = Fraction(1)

        remainder = Fraction(1) - total_fixed

        # --- 3. ASABA (Residuaries taking remainder) ---
        if remainder > 0:
            if sons > 0:
                total_parts = (sons * 2) + daughters
                if daughters > 0:
                    shares["son"] = (remainder * sons * 2) / total_parts
                    shares["daughter"] = shares.get("daughter", Fraction(0)) + (remainder * daughters) / total_parts
                else:
                    shares["son"] = remainder
                remainder = 0
            elif daughters > 0 and siss > 0 and father == 0 and pat_gf == 0 and bros == 0:
                # Full Sisters become Asaba ma'al Ghayr (Residuary with daughters)
                shares["sister"] = shares.get("sister", Fraction(0)) + remainder
                remainder = 0
            elif daughters > 0 and pat_siss > 0 and father == 0 and pat_gf == 0 and bros == 0 and siss == 0 and pat_bros == 0:
                # Paternal Sisters become Asaba with daughters if no full sisters
                shares["paternal_sister"] = shares.get("paternal_sister", Fraction(0)) + remainder
                remainder = 0
            elif father > 0:
                shares["father"] = shares.get("father", Fraction(0)) + remainder
                remainder = 0
            elif pat_gf > 0:
                shares["paternal_grandfather"] = shares.get("paternal_grandfather", Fraction(0)) + remainder
                remainder = 0
            elif bros > 0:
                if not is_mushtarakah: # If Mushtarakah is active, they're already in the 1/3 pool.
                    total_parts = (bros * 2) + siss
                    if siss > 0:
                        shares["brother"] = (remainder * bros * 2) / total_parts
                        shares["sister"] = shares.get("sister", Fraction(0)) + (remainder * siss) / total_parts
                    else:
                        shares["brother"] = remainder
                    remainder = 0
            elif pat_bros > 0:
                total_parts = (pat_bros * 2) + pat_siss
                if pat_siss > 0:
                    shares["paternal_brother"] = (remainder * pat_bros * 2) / total_parts
                    shares["paternal_sister"] = shares.get("paternal_sister", Fraction(0)) + (remainder * pat_siss) / total_parts
                else:
                    shares["paternal_brother"] = remainder
                remainder = 0
            elif pat_uncle > 0:
                shares["paternal_uncle"] = remainder
                remainder = 0

        # --- 4. RADD (Return if Undersubscribed) & DHAWU AL-ARHAM ---
        dhawu_al_arham = ["maternal_uncle", "maternal_grandfather"]
        if remainder > 0:
            # Check for primary eligible heirs to return excess to (spouses and distant kindred don't participate primarily in Radd)
            radd_eligible_shares = sum(v for k, v in shares.items() if k not in ["husband", "wife"] + dhawu_al_arham)
            
            if radd_eligible_shares > 0:
                multiplier = remainder / radd_eligible_shares
                for k in list(shares.keys()):
                    if k not in ["husband", "wife"] + dhawu_al_arham:
                        shares[k] += shares[k] * multiplier
                remainder = 0
            else:
                # Dhawu al-Arham (Distant Kindred): Inherit ONLY if no primary heirs (except spouse) survive
                if mat_gf > 0:
                    shares["maternal_grandfather"] = remainder
                    remainder = 0
                elif mat_uncle > 0:
                    shares["maternal_uncle"] = remainder
                    remainder = 0

        # --- 5. RESOLVE POOLED SHARES (Grandmothers & Siblings) ---
        
        # Split Grandmothers' 1/6
        if "grandmothers_shared" in shares:
            gm_share = shares["grandmothers_shared"]
            num_gms = sum(1 for condition in [mat_gm > 0, (pat_gm > 0 and father == 0)] if condition)
            if num_gms > 0:
                per_gm = gm_share / num_gms
                if mat_gm > 0: shares["maternal_grandmother"] = per_gm
                if pat_gm > 0 and father == 0: shares["paternal_grandmother"] = per_gm
            del shares["grandmothers_shared"]

        # Split Al-Mushtarakah Pool (Equal shares to maternal and full siblings - no 2:1 ratio)
        if "mushtarakah_pool" in shares:
            pool_share = shares["mushtarakah_pool"]
            total_people = mat_bros + mat_siss + bros + siss
            per_person = pool_share / total_people
            
            if mat_bros > 0: shares["maternal_brother"] = per_person * mat_bros
            if mat_siss > 0: shares["maternal_sister"] = per_person * mat_siss
            if bros > 0: shares["brother"] = per_person * bros
            if siss > 0: shares["sister"] = per_person * siss
            
            del shares["mushtarakah_pool"]
            
        # Split Standard Maternal Siblings Fixed Share (Equal shares)
        elif "maternal_siblings" in shares:
            per_person = shares["maternal_siblings"] / mat_total
            if mat_bros > 0: shares["maternal_brother"] = per_person * mat_bros
            if mat_siss > 0: shares["maternal_sister"] = per_person * mat_siss
            del shares["maternal_siblings"]

        return shares
