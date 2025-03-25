# Dynamic Fee for Reducing Impermanent Loss in Decentralized Exchanges

This repository contains the code and simulation framework for the paper "Dynamic Fee for Reducing Impermanent Loss in Decentralized Exchanges".


## Project Structure

- **User types** are implemented in [`user_types/`](./user_types)
    - `base.py` – abstract base class for user types
    - `informed_user.py` – informed user
    - `uninformed_user.py` – uninformed user

- **Fee algorithms** are implemented in [`fee_algorithm/`](./fee_algorithm)
    - `base.py` – abstract base class for fees
    - `fixed_fee.py` – FX -- fixed symmetric fee (baseline)
    - `adaptive_fee_based_on_block_price_move.py` – BA -- block-adaptive fee
    - `based_on_trade_count_fee.py` – DA -- deal-adaptive fee
    - `discrete_fee_perfect_oracle.py` – OB -- oracle-based benchmark
    - There are also other algorithms in this repository, but they are not included in the paper (mostly due to poor performance)
    
- **Simulation framework** is implemented in [`simulation/`](./simulation)

- **Configuration** 
    - We use one python class config to configure all parameters of the single simulation run.
    - The config is stored in [`config.py`](./config.py)

## Setup

This project requires Python 3.12. 

Here's how to set up the development environment:

1. Make sure you have Python 3.12 installed:
   ```bash
   python --version
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/your-username/dynamic-fee-dex.git
   cd dynamic-fee-dex
   ```

3. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. You're all set!

## Running Experiments

The repository includes scripts for running both real-data and synthetic data experiments from the paper.

### Real-Data Experiments

To run experiments with real market data, launch [`visualizations/fee_algorithms_comparison.ipynb`](./visualizations/fee_algorithms_comparison.ipynb)

### Synthetic Data Experiments

To run experiments with synthetic data
- Generate synthetic data parameters using [`visualizations/synthetic_data_example.ipynb`](./visualizations/synthetic_data_example.ipynb)
- Run experiments using [`visualizations/fee_algorithms_comparison_synth_data.ipynb`](./visualizations/fee_algorithms_comparison_synth_data.ipynb)


### Running Tests

The project uses pytest for testing. To run all tests:

```bash
pytest tests/
```

To run specific test files:

```bash
pytest tests/test_informed_user.py
pytest tests/test_user_action_correctness.py
```

## Citation

If you use this work, please cite:

```bibtex
@inproceedings{Lebedeva2025DexDynamicFee,
  title     = {Dynamic Fee for Reducing Impermanent Loss in Decentralized Exchanges},
  author    = {Lebedeva Irina and Umnov Dmitrii and Yanovich Yury and Melnikov Ignat and Ovchinnikov George},
  booktitle = {Proceedings of the IEEE International Conference on Blockchain and Cryptocurrency (ICBC)},
  year      = {2025}
}
