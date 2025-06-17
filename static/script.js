const CATEGORY_COLORS = {
  "Positive": "#4CAF50",
  "Negative": "#F44336",
  "Spam": "#9E9E9E",
  "Question": "#2196F3",
  "Feedback": "#FF9800",
  "Promotional": "#9C27B0",
  "All": "#fff"
};

async function submitVideoUrl() {
    const url = document.getElementById("videoUrlInput").value;
    // document.getElementById("videoStats").innerText = "Loading...";

    const res = await fetch("/submit-url", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ videoUrl: url })
    });

    const stats = await res.json();
    createStatsGraph(stats)

    // Refresh videos list
    fetchVideos();
}

async function fetchVideos() {
    const res = await fetch("/videos");
    const videos = await res.json();
    const list = document.getElementById("videoList");
    list.innerHTML = "";

    videos.forEach(v => {
        const div = document.createElement("div");
        div.className = "video-item";
        div.onclick = () => fetchCategoryStats(v.videoId);

        div.innerHTML = `
            <img src="${v.thumbnail}" alt="Thumbnail" class="thumbnail">
            <div class="video-info">
                <h4>${v.title}</h4>
                <p>${v.total_comments} comments</p>
            </div>
        `;
        list.appendChild(div);
    });
}

async function fetchCategoryStats(videoId) {
    localStorage.setItem("videoId", videoId);
    const res = await fetch(`/category-stats?videoId=${videoId}`);
    const stats = await res.json();
    createStatsGraph(stats)
}

function getRandomColor() {
  return '#' + Math.floor(Math.random()*16777215).toString(16);
}

async function createStatsGraph(stats) {
    const section = document.getElementById('second-section');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
    // Filter out "All"
    const filtered = stats.filter(s => s.category && s.category !== "All");

    // Pie chart data
    const labels = filtered.map(s => s.category);
    const counts = filtered.map(s => s.count);

    // Draw pie chart
    const ctx = document.querySelector("#pieChart canvas").getContext("2d");
    if(window.myPie) window.myPie.destroy(); // destroy existing chart if any
    window.myPie = new Chart(ctx, {
        type: 'pie',
        data: {
        labels,
        datasets: [{
            data: counts,
            backgroundColor: labels.map(label => CATEGORY_COLORS[label] || getRandomColor())
        }]
        }
    });

    // Find the "All" category stats
    const allStats = stats.find(s => s.category === "All") || {};

    // Update ranges and display values
    const sentimentInput = document.getElementById("sentimentRange");
    const toxicityInput = document.getElementById("toxicityRange");
    const sentimentVal = document.getElementById("sentimentValue");
    const toxicityVal = document.getElementById("toxicityValue");

    sentimentInput.value = allStats.avg_sentiment ?? 0;
    toxicityInput.value = allStats.avg_toxicity ?? 0;
    sentimentVal.innerText = sentimentInput.value;
    toxicityVal.innerText = toxicityInput.value;

    checkSubCategorization()
}

async function checkSubCategorization() {
    const videoId = localStorage.getItem("videoId");
    const res = await fetch(`/check-subcategory?videoId=${videoId}`);
    const exists = await res.json();

    if(exists) {
        fetchSubCategoryStats(videoId)
        fetchKeywordStats(videoId)
        document.getElementById('third-section').style.display = 'block';
        document.getElementById("subcategorizeBtn").style.display = "none";
        document.getElementById("subcategory-stats-div").style.display = "block";
        document.getElementById("keyword-stats-div").style.display = "block";
        document.getElementById("showAllCommentsBtn").style.display = "inline-block";
    } else {
        document.getElementById("subcategorizeBtn").style.display = "inline-block";
        document.getElementById("subcategory-stats-div").style.display = "none";
        document.getElementById("keyword-stats-div").style.display = "none";
        document.getElementById("showAllCommentsBtn").style.display = "none";
    }
}

async function runSubcategorization() {
    const videoId = localStorage.getItem("videoId");
    if (!videoId) {
        alert("No video selected");
        return;
    }

    const res = await fetch("/subcategorize", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `videoId=${videoId}`
    });
    const result = await res.json();
    // alert(result.message);

    if (result.code === 200) {
        fetchSubCategoryStats(videoId);
        fetchKeywordStats(videoId);
        document.getElementById('third-section').style.display = 'block';
        const section = document.getElementById('third-section');
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
        document.getElementById("showAllCommentsBtn").style.display = "inline-block";
    }
}

async function fetchSubCategoryStats(videoId) {
    const res = await fetch(`/sub-category-stats?videoId=${videoId}`);
    const data = await res.json();

    const labels = ["All"];
    const parents = [""];
    const values = [0];

    data.forEach(group => {
        labels.push(group.category);
        parents.push("All");
        values.push(0);
        group.subcategories.forEach(sub => {
        labels.push(sub.subCategory);
        parents.push(group.category);
        values.push(sub.count);
        });
    });

    const layout = {
        paper_bgcolor: "#212121",   
        plot_bgcolor: "blue",
        height: 750,
        font: {
            size: 24
        }    
    };

    const trace = {
        type: "treemap",
        labels,
        parents,
        values,
        textinfo: "label+value",
        outsidetextfont: { size: 16, color: "#377eb8" },
        marker: {
            colors: labels.map((label, i) => {
                const parent = parents[i];
                return CATEGORY_COLORS[label] || CATEGORY_COLORS[parent] || getRandomColor();
            })
        }
    };
    document.getElementById("subcategory-stats-div").style.display = "block";
    Plotly.newPlot("treemap", [trace], layout);
}

async function fetchKeywordStats(videoId) {
    const res = await fetch(`/keyword-stats?videoId=${videoId}`);
    const data = await res.json();

    const keywords = data.map(d => d.keyword);
    const counts = data.map(d => d.count);

    const trace = {
        x: keywords,
        y: counts,
        type: 'bar',
        marker: { color: '#4caf50' }
    };

    const layout = {
        title: 'Top Keywords',
        xaxis: { title: 'Keyword' },
        yaxis: { title: 'Count' },
        paper_bgcolor: "#212121",   // background around the plot
        plot_bgcolor: "#212121",     // background inside the plotting area
        font: { color: "#ffffff" }
    };
    document.getElementById("keyword-stats-div").style.display = "block";
    Plotly.newPlot('keywordBarChart', [trace], layout);
}

async function showAllComments() {
    const videoId = localStorage.getItem("videoId");
    const resComments = await fetch(`/get-comments?videoId=${videoId}`);
    const dataComments = await resComments.json();
    console.log(dataComments)
    displayComments(dataComments);

    const resCatSubcat = await fetch(`/get-categories-subcategories?videoId=${videoId}`);
    const dataCatSubcat = await resCatSubcat.json();
    localStorage.setItem("dataCatSubcat", JSON.stringify(dataCatSubcat));

    const categorySelect = document.getElementById("categorySelect");
    const subcategorySelect = document.getElementById("subcategorySelect");

    categorySelect.innerHTML = '<option value="">Select Category</option>';
    subcategorySelect.innerHTML = '<option value="">Select Subcategory</option>';

    dataCatSubcat.categories.forEach(cat => {
        const option = document.createElement("option");
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });

    dataCatSubcat.subcategories.forEach(sub => {
        const option = document.createElement("option");
        option.value = sub;
        option.textContent = sub;
        subcategorySelect.appendChild(option);
    });
    const section = document.getElementById('comments-playground');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
}

async function sortComments() {
    const category = document.getElementById('categorySelect').value || '';
    const subcategory = document.getElementById('subcategorySelect').value || '';
    
    const videoId = localStorage.getItem("videoId");
    const res = await fetch(`/get-comments?videoId=${videoId}&category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}`);
    const data = await res.json()
    displayComments(data)

    document.getElementById("summaryDrawer").style.display = "block";
    document.getElementById("close-summary-btn").style.display = "inline-block";
    document.getElementById("rulesDrawer").style.display = "none";
    document.getElementById("commentsList").style.width = "65%";

    const resSummary = await fetch(`/summarize-comments?videoId=${videoId}&category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}`);
    const dataSummary = await resSummary.json();
    document.getElementById("categorySummary").innerHTML = `${dataSummary.category_summary || "Select Category Sort"}`
    document.getElementById("subcategorySummary").innerHTML = `${dataSummary.subcategory_summary || "Select SubCategory Sort"}`
    document.getElementById("close-summary-btn").style.display = "inline-block";
}

async function displayComments(data) {
    const container = document.getElementById("commentsList");
    container.innerHTML = "";

    data.forEach(comment => {
        const div = document.createElement("div");
        div.classList.add("comment-item");
        if (!comment.display) div.classList.add("red-border");
        div.innerHTML = `
            <p><strong>Comment:</strong> ${comment.textOriginal}</p>
            <p><strong>Subcategory:</strong> ${comment.subCategory || 'N/A'}</p>
            <br><br>
            <div class="meta">
                <span>Likes: ${comment.likeCount}</span>
                <span>Replies: ${comment.totalReplyCount}</span>
                <span>Sentiment: ${comment.sentiment}</span>
                <span>Toxicity: ${comment.toxicity}</span>
                <span>Updated: ${comment.updatedAt}</span>
            </div>
            ${!comment.display ? `
                <div class="warning">
                <strong>Current applied rules will not display this comment:</strong>
                <ul>${comment.displayReasons.map(r => `<li>${r}</li>`).join('')}</ul>
                </div>` : ""}
            `;
        
        container.appendChild(div);
    });
}

const selectedCategories = [];
const selectedSubcategories = [];
const selectedWords = [];
const selectedPhrases = [];

function initRulesDrawer() {
    const data = JSON.parse(localStorage.getItem("dataCatSubcat"));
    const catDiv = document.getElementById("categoryChips");
    const subDiv = document.getElementById("subcategoryChips");

    catDiv.innerHTML = '';
    subDiv.innerHTML = '';

    data.categories.forEach(cat => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = cat;
        chip.onclick = () => toggleSelection(chip, selectedCategories, cat);
        catDiv.appendChild(chip);
    });

    data.subcategories.forEach(sub => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = sub;
        chip.onclick = () => toggleSelection(chip, selectedSubcategories, sub);
        subDiv.appendChild(chip);
    });
}

function toggleSelection(chip, array, value) {
    const index = array.indexOf(value);
    if (index > -1) {
        array.splice(index, 1);
        chip.classList.remove("selected");
    } else {
        array.push(value);
        chip.classList.add("selected");
    }
}

document.getElementById("wordInput").addEventListener("keydown", e => {
    if (e.key === "Enter") {
        const word = e.target.value.trim();
        if (word && !selectedWords.includes(word)) {
        selectedWords.push(word);
        updateList("wordList", selectedWords);
        }
        e.target.value = "";
    }
});

document.getElementById("phraseInput").addEventListener("keydown", e => {
    if (e.key === "Enter") {
        const phrase = e.target.value.trim();
        if (phrase && !selectedPhrases.includes(phrase)) {
        selectedPhrases.push(phrase);
        updateList("phraseList", selectedPhrases);
        }
        e.target.value = "";
    }
});

function updateList(divId, items) {
    document.getElementById(divId).innerHTML = items.map(i => `<span class="chip">${i}</span>`).join('');
}

async function createRules() {
    const videoId = localStorage.getItem("videoId");
    const formData = new FormData();
    formData.append("videoId", videoId);
    formData.append("categories", JSON.stringify(selectedCategories));
    formData.append("subcategories", JSON.stringify(selectedSubcategories));
    formData.append("keywords", JSON.stringify(keywords));
    formData.append("phrases", JSON.stringify(phrases));

    const res = await fetch("/create-rules", {
        method: "POST",
        body: formData
    });
    const data = await res.json();
    if (data.code === 200) {
        document.querySelector('button[onclick="applyRules()"]').style.display = "inline-block";
    }
}

async function applyRules() {
    const videoId = localStorage.getItem("videoId");
    const res = await fetch(`/apply-rules?videoId=${videoId}`);
    const exists = await res.json();

    if(exists.code === 200) {
        const resComments = await fetch(`/get-comments?videoId=${videoId}`);
        const dataComments = await resComments.json();
        displayComments(dataComments);
    }
}

async function showRules() {
    document.getElementById("rulesDrawer").style.display = "block";
    document.getElementById("summaryDrawer").style.display = "none";
    document.getElementById("close-summary-btn").style.display = "none";
    document.getElementById("commentsList").style.width = "65%";
    document.getElementById("show-rules-btn").style.display = "none";
    document.getElementById("close-rules-btn").style.display = "inline-block";
    initRulesDrawer();

    const videoId = localStorage.getItem("videoId");
    const checkRes = await fetch(`/check-rules?videoId=${videoId}`);
    const exists = await checkRes.json();

    if (exists) {
        const res = await fetch(`/get-video-rules?videoId=${videoId}`);
        const rules = await res.json();
        console.log(rules)

        rules.blockCategories.forEach(cat => {
            selectedCategories.push(cat);
            const chip = [...document.querySelectorAll('#categoryChips .chip')].find(c => c.textContent === cat);
            if (chip) chip.classList.add("selected");
        });

        rules.blockSubCategories.forEach(sub => {
            selectedSubcategories.push(sub);
            const chip = [...document.querySelectorAll('#subcategoryChips .chip')].find(c => c.textContent === sub);
            if (chip) chip.classList.add("selected");
        });

        selectedWords.push(...rules.notAllowedWords);
        selectedPhrases.push(...rules.contentRules);
        updateList("wordList", selectedWords);
        updateList("phraseList", selectedPhrases);
    }
}

function closeRules() {
    document.getElementById("rulesDrawer").style.display = "none";
    document.getElementById("commentsList").style.width = "100%";
    document.getElementById("close-rules-btn").style.display = "none";
    document.getElementById("show-rules-btn").style.display = "inline-block";
}

function closeSummary() {
    document.getElementById("summaryDrawer").style.display = "none";
    document.getElementById("commentsList").style.width = "100%";
    document.getElementById("close-summary-btn").style.display = "none";
    document.getElementById("show-rules-btn").style.display = "inline-block";
}

async function checkRulesAndToggleCompare(videoId) {
    const res = await fetch(`/check-rules?videoId=${videoId}`);
    const isAllowed = await res.json();
    document.getElementById("compareBtn").style.display = isAllowed ? "inline-block" : "none";
}

window.onload = fetchVideos;

{}