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
        grandpa = h.get("grandfather", 0)
        grandma = h.get("grandmother", 0)
        bros = h.get("brother", 0)
        siss = h.get("sister", 0)
        mat_bros = h.get("maternal_brother", 0)
        mat_siss = h.get("maternal_sister", 0)
        pat_uncle = h.get("paternal_uncle", 0)
        mat_uncle = h.get("maternal_uncle", 0)

        # Fiqh Conditions
        children_exist = (sons + daughters) > 0
        male_descendants = sons > 0
        sibling_count = bros + siss + mat_bros + mat_siss
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

        # Mother & Grandmother
        if mother > 0:
            share = Fraction(1, 6) if (children_exist or siblings_exist) else Fraction(1, 3)
            # Umariyyatain simplified: Mother takes 1/3 of remainder if only parents and spouse survive
            if not children_exist and sibling_count == 0 and father > 0 and grandpa == 0:
                spouse_share = shares.get("husband", Fraction(0)) + shares.get("wife", Fraction(0))
                share = Fraction(1, 3) * (Fraction(1) - spouse_share)
            shares["mother"] = share
            total_fixed += share
        elif grandma > 0:
            share = Fraction(1, 6)
            shares["grandmother"] = share
            total_fixed += share

        # Father & Grandfather
        if father > 0:
            if male_descendants:
                share = Fraction(1, 6)
                shares["father"] = share
                total_fixed += share
            elif daughters > 0:
                share = Fraction(1, 6) # Gets 1/6 + Asaba later
                shares["father"] = share
                total_fixed += share
        elif grandpa > 0:
            if male_descendants:
                share = Fraction(1, 6)
                shares["grandfather"] = share
                total_fixed += share
            elif daughters > 0:
                share = Fraction(1, 6)
                shares["grandfather"] = share
                total_fixed += share

        # Daughters (if no sons)
        if daughters > 0 and sons == 0:
            share = Fraction(1, 2) if daughters == 1 else Fraction(2, 3)
            shares["daughter"] = share
            total_fixed += share

        # Maternal Siblings (Blocked by children, father, and grandfather)
        if not children_exist and father == 0 and grandpa == 0:
            mat_total = mat_bros + mat_siss
            if mat_total > 0:
                share = Fraction(1, 6) if mat_total == 1 else Fraction(1, 3)
                shares["maternal_siblings"] = share
                total_fixed += share

        # Full Sisters (Fixed share if no sons, daughters, father, grandpa, or full brothers)
        if daughters == 0 and sons == 0 and father == 0 and grandpa == 0 and bros == 0:
            if siss > 0:
                share = Fraction(1, 2) if siss == 1 else Fraction(2, 3)
                shares["sister"] = share
                total_fixed += share

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
            elif daughters > 0 and siss > 0 and father == 0 and grandpa == 0 and bros == 0:
                # Sisters become Asaba ma'al Ghayr (Residuary with daughters)
                shares["sister"] = shares.get("sister", Fraction(0)) + remainder
                remainder = 0
            elif father > 0:
                shares["father"] = shares.get("father", Fraction(0)) + remainder
                remainder = 0
            elif grandpa > 0:
                shares["grandfather"] = shares.get("grandfather", Fraction(0)) + remainder
                remainder = 0
            elif bros > 0:
                total_parts = (bros * 2) + siss
                if siss > 0:
                    shares["brother"] = (remainder * bros * 2) / total_parts
                    shares["sister"] = shares.get("sister", Fraction(0)) + (remainder * siss) / total_parts
                else:
                    shares["brother"] = remainder
                remainder = 0
            elif pat_uncle > 0:
                shares["paternal_uncle"] = remainder
                remainder = 0

        # --- 4. RADD (Return if Undersubscribed) ---
        if remainder > 0:
            non_spouse_shares = sum(v for k, v in shares.items() if k not in ["husband", "wife", "maternal_uncle"])
            if non_spouse_shares > 0:
                multiplier = remainder / non_spouse_shares
                for k in list(shares.keys()):
                    if k not in ["husband", "wife", "maternal_uncle"]:
                        shares[k] += shares[k] * multiplier
                remainder = 0
            else:
                # Dhawu al-Arham: Inherit ONLY if no one else exists except a spouse
                if mat_uncle > 0:
                    shares["maternal_uncle"] = remainder
                    remainder = 0

        # Split Maternal Siblings share equally among male and female (Fiqh rule)
        if "maternal_siblings" in shares:
            mat_total = mat_bros + mat_siss
            per_person = shares["maternal_siblings"] / mat_total
            if mat_bros > 0:
                shares["maternal_brother"] = per_person * mat_bros
            if mat_siss > 0:
                shares["maternal_sister"] = per_person * mat_siss
            del shares["maternal_siblings"]

        return shares
