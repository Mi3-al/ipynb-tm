import json
import glob
import os
import urllib.parse

# ユーザー設定（リポジトリ情報に合わせて変更してください）
GITHUB_USER = "Mi3-al"
REPO_NAME = "ipynb-tm"
BRANCH = "main"

def extract_notebook_info(filepath):
    """
    Notebookの最初のMarkdownセルからタイトルと説明（Objective）を抽出する
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
            
        first_md_cell = next((cell for cell in nb['cells'] if cell['cell_type'] == 'markdown'), None)
        
        if not first_md_cell:
            return os.path.basename(filepath), "No description available."

        source = "".join(first_md_cell['source'])
        lines = source.split('\n')
        
        # タイトル抽出 (# で始まる行)
        title = os.path.basename(filepath)
        for line in lines:
            if line.strip().startswith('# '):
                title = line.strip().replace('# ', '').strip()
                break
        
        # 説明抽出 (**Objective:** を探す、なければタイトルの次の行などを採用)
        description = ""
        for line in lines:
            if "**Objective:**" in line:
                # **Objective:** 以降のテキストを取得
                description = line.split("**Objective:**")[1].strip()
                break
        
        if not description:
            # Objectiveが見つからない場合は、タイトル以外の最初の空行でないテキストを利用
            for line in lines:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('#'):
                    description = clean_line
                    break
                    
        return title, description
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return os.path.basename(filepath), "Error reading file."

def generate_readme():
    notebooks = sorted(glob.glob("*.ipynb"))
    
    # おしゃれなヘッダー
    content = [
        "# 📚 Interactive Notebooks Collection",
        "",
        "自動生成されたインデックスです。各NotebookはGoogle Colabで直接実行できます。",
        "",
        "| Notebook | Description | Open in Colab |",
        "| :--- | :--- | :---: |"
    ]
    
    for nb_path in notebooks:
        title, desc = extract_notebook_info(nb_path)
        
        # GitHubとColabのURL生成
        github_url = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/blob/{BRANCH}/{nb_path}"
        colab_url = f"https://colab.research.google.com/github/{GITHUB_USER}/{REPO_NAME}/blob/{BRANCH}/{nb_path}"
        
        # 行を追加
        colab_badge = f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({colab_url})"
        # 説明が長すぎる場合はカット
        if len(desc) > 100:
            desc = desc[:97] + "..."
            
        content.append(f"| **{title}** | {desc} | {colab_badge} |")
        
    content.append("")
    content.append(f"Last updated: {os.popen('date -u').read().strip()}")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(content))

if __name__ == "__main__":
    generate_readme()