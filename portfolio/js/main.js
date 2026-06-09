document.addEventListener("DOMContentLoaded", () => {
    // Stage Elements
    const stages = [
        document.getElementById("stage-1"),
        document.getElementById("stage-2"),
        document.getElementById("stage-3"),
        document.getElementById("stage-4")
    ];
    
    const transitionOverlay = document.getElementById("transition-overlay");
    
    // Stage 1 Elements
    const dialogueText1 = document.getElementById("dialogue-text-1");
    const nextBtn1 = document.getElementById("next-stage1");
    const doorHotspot1 = document.querySelector("#stage-1 .door-hotspot");
    
    // Stage 2 & 3 Elements
    const enterDoorBtn = document.getElementById("enter-door-btn");
    const usePcBtn = document.getElementById("use-pc-btn");
    
    // Stage 4 Elements
    const bootSequence = document.getElementById("boot-sequence");
    const bootText = document.getElementById("boot-text");
    const osMenu = document.getElementById("os-menu");
    const menuBtns = document.querySelectorAll(".menu-btn");
    const closeBtns = document.querySelectorAll(".close-btn");
    
    // Containers
    const projectsContainer = document.getElementById("projects-container");
    const skillsContainer = document.getElementById("skills-container");
    const connectContainer = document.getElementById("connect-container");

    // Utilities
    function switchStage(fromIndex, toIndex, callback = null) {
        transitionOverlay.classList.add("blackout");
        
        setTimeout(() => {
            stages[fromIndex].classList.remove("active");
            stages[toIndex].classList.add("active");
            transitionOverlay.classList.remove("blackout");
            if (callback) callback();
        }, 1000);
    }

    function typeText(element, text, speed = 30, callback = null) {
        element.textContent = "";
        let i = 0;
        function typeWriter() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, speed);
            } else {
                if (callback) callback();
            }
        }
        typeWriter();
    }

    // Initialize Content
    function renderProjects() {
        portfolioData.projects.forEach(p => {
            const card = document.createElement("div");
            card.className = "project-card";
            card.innerHTML = `
                <h3>${p.title}</h3>
                <p>${p.description}</p>
                <div class="project-links">
                    <a href="${p.github}" target="_blank">GitHub</a>
                    <a href="${p.demo}" target="_blank">Demo</a>
                </div>
            `;
            projectsContainer.appendChild(card);
        });
    }

    function renderSkills() {
        let terminalHTML = `> aayushi --skills\nLoading skills matrix...\n\n`;
        for (const [category, skillsArr] of Object.entries(portfolioData.skills)) {
            terminalHTML += `<div class="skill-category">
                <span>[${category}]</span>: ${skillsArr.join(" | ")}
            </div>`;
        }
        terminalHTML += `> <span class="blink">_</span>`;
        skillsContainer.innerHTML = terminalHTML;
        
        // Add a simple blink effect to the terminal cursor
        setInterval(() => {
            const cursor = document.querySelector(".blink");
            if(cursor) cursor.style.opacity = cursor.style.opacity === "0" ? "1" : "0";
        }, 500);
    }

    function renderLinks() {
        portfolioData.links.forEach(l => {
            const a = document.createElement("a");
            a.className = "connect-link";
            a.href = l.url;
            a.target = "_blank";
            a.textContent = l.name;
            connectContainer.appendChild(a);
        });
    }

    renderProjects();
    renderSkills();
    renderLinks();

    // Event Listeners
    
    // Stage 1 logic
    setTimeout(() => {
        typeText(dialogueText1, portfolioData.dialogue, 30, () => {
            nextBtn1.classList.remove("hidden");
        });
    }, 1000);

    nextBtn1.addEventListener("click", () => {
        switchStage(0, 1); // Move to House transition
    });
    
    doorHotspot1.addEventListener("click", () => {
        if (!nextBtn1.classList.contains("hidden")) {
            switchStage(0, 1);
        }
    });

    // Stage 2 logic
    enterDoorBtn.addEventListener("click", () => {
        switchStage(1, 2); // Move to Magic Room
    });

    // Stage 3 logic
    usePcBtn.addEventListener("click", () => {
        switchStage(2, 3, () => {
            // Start Boot Sequence
            const bootString = `Initializing kernel...\nLoading memory modules...\nMounting file systems... OK\nStarting Aayushi OS...\nWelcome back, Administrator.`;
            typeText(bootText, bootString, 40, () => {
                setTimeout(() => {
                    bootSequence.classList.add("hidden");
                    osMenu.classList.remove("hidden");
                }, 1000);
            });
        });
    });

    // Stage 4 UI logic
    menuBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            document.getElementById(targetId).classList.remove("hidden");
        });
    });

    closeBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.target.closest(".modal").classList.add("hidden");
        });
    });
});
