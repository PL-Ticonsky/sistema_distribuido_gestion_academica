(function () {
    const toggles = document.querySelectorAll("[data-condor-sidebar-toggle]");
    const backdrop = document.querySelector("[data-condor-sidebar-backdrop]");
    const body = document.body;
    const root = document.documentElement;
    const storageKey = "condor.sidebar";
    const mobileQuery = window.matchMedia("(max-width: 992px)");

    function isCollapsed() {
        return body.classList.contains("condor-sidebar-collapsed");
    }

    function setExpandedState() {
        const expanded = mobileQuery.matches
            ? body.classList.contains("condor-sidebar-open")
            : !isCollapsed();

        toggles.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(expanded));
        });
    }

    function closeMobileSidebar() {
        body.classList.remove("condor-sidebar-open");
        setExpandedState();
    }

    function applyStoredState() {
        let storedValue = null;

        try {
            storedValue = localStorage.getItem(storageKey);
        } catch (error) {
            storedValue = null;
        }

        body.classList.remove("condor-sidebar-collapsed");

        if (storedValue === "collapsed" && !mobileQuery.matches) {
            body.classList.add("condor-sidebar-collapsed");
        }

        root.classList.remove("condor-sidebar-pref-collapsed");
        setExpandedState();
    }

    toggles.forEach((toggle) => {
        toggle.addEventListener("click", () => {
            if (mobileQuery.matches) {
                body.classList.toggle("condor-sidebar-open");
                setExpandedState();
                return;
            }

            body.classList.toggle("condor-sidebar-collapsed");

            try {
                localStorage.setItem(
                    storageKey,
                    isCollapsed() ? "collapsed" : "expanded",
                );
            } catch (error) {
                // Sidebar preference is optional.
            }

            setExpandedState();
        });
    });

    if (backdrop) {
        backdrop.addEventListener("click", closeMobileSidebar);
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMobileSidebar();
        }
    });

    mobileQuery.addEventListener("change", () => {
        closeMobileSidebar();
        applyStoredState();
    });

    applyStoredState();
})();
