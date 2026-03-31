# Electric Machines Virtual Lab

Electric Machines virtual lab for EEE students built with Streamlit.

## Features
- Aim and theory section
- Lab Manual mode (aim, apparatus, procedure, observations, viva)
- Proper virtual lab modules with components, wiring, procedure, observation sheet, and result panel
- Student login/register and progress dashboard
- Login available in sidebar and Dashboard page
- Demo user: `student1` / `eee123`
- Virtual instrument: tachometer simulator
- Virtual instrument: insulation tester simulator
- Virtual instrument: power analyzer simulator
- Electric machines calculator: synchronous speed and slip
- Electric machines calculator: transformer efficiency
- Electric machines calculator: DC motor speed estimate
- Quiz section
- Feedback section

## Files to upload to GitHub
- `app.py`
- `requirements.txt`
- `README.md`
- `.gitignore`

Note: `.venv` and `lab_state.json` should not be uploaded.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push these files to your GitHub repo.
2. Go to `https://share.streamlit.io`.
3. Select your repo.
4. Main file path: `app.py`.
5. Click Deploy.
