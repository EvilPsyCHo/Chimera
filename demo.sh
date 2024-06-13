activate chimera
rm -rf Chimera
git clone https://github.com/EvilPsyCHo/Chimera.git
cd Chimera
pip install -r requirements.txt
OPENAI_API_KEY="sk-DuN7MOXUXb4NIGCN300a03E7129947718979198cEe1385D7"
OPENAI_BASE_URL="https://api.xi-ai.cn/v1"
MODEL="gpt-4o"
streamlit run webui.py