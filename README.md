# 🕌 Islamic Inheritance Calculator (Faraid Engine)

A web-based tool that calculates Islamic inheritance shares (Faraid) according to Shariah law. This project leverages **PyScript** to run a comprehensive Python calculation engine entirely in the browser—no backend server required.

## 🚀 Live Demo

You can access and use the calculator directly here:  
**[Islamic Inheritance Calculator](https://sahlahadesina.github.io/inheritance-calc/)**

Because this project uses PyScript, there is nothing to download or install. Simply click the link above, enter the estate details, and the Python engine will execute locally within your browser.

## ✨ Features

* **Comprehensive Heir Selection:** Supports spouses, descendants (sons, daughters), ascendants (parents, maternal/paternal grandparents), siblings (full, paternal, and maternal), and uncles.
* **Ashab al-Furud (Fixed Shares):** Automatically assigns the correct Qur'anic fractional shares based on the presence or absence of other relatives.
* **Al-Asaba (Residuaries):** Calculates the remaining estate for residuaries (e.g., sons, full brothers, fathers) after fixed shares are distributed.
* **Complex Fiqh Rulings Handled:**
  * **'Awl (Oversubscription):** Proportionally reduces shares when the total fixed fractions exceed the estate.
  * **Radd (Return):** Returns excess estate to primary fixed sharers when the estate is undersubscribed.
  * **Al-Mushtarakah / Himariyya:** Correctly handles the special "Donkey Case" where full brothers share the 1/3 pool equally with maternal siblings.
  * **Umariyyatain:** Adjusts the mother's share to 1/3 of the *remainder* in specific parent-spouse scenarios.
  * **Total Exclusion (Hajb):** Accurately blocks distant relatives when closer ones are present (e.g., Full Brothers blocking Paternal Brothers; Fathers blocking Grandfathers).

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3
* **Logic/Engine:** Python 3
* **Bridge:** [PyScript](https://pyscript.net/) (Allows Python to run directly in the HTML via WebAssembly)

## 📂 Project Structure

* `index.html`: The main user interface. Contains the PyScript configuration, CSS styling, and form inputs.
* `engine.py`: The core Fiqh logic. Handles all fractional math using Python's `fractions.Fraction` module and evaluates the inheritance rules.

## 💡 How it Works

1. The user inputs the total estate value, the gender of the deceased, and the number of surviving relatives.
2. The UI passes this data to the `Engine` class in `engine.py`.
3. The engine assesses Fiqh conditions (e.g., "Are there male descendants?", "Are there multiple siblings?").
4. It distributes **Fixed Shares** first.
5. It checks for **'Awl** (if total > 1) or applies **Al-Mushtarakah** if conditions are met.
6. It distributes the remainder to the **Asaba** (residuaries).
7. If there is still a remainder and no Asaba, it applies **Radd** (return) to the eligible fixed sharers.
8. The final fractions and exact monetary values are returned and displayed.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request to improve the calculations or the interface.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
