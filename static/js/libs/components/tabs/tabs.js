export function initTabs() {
    return {
        activeTab: 'tab-besu-poa',
        switchTabs(e) {
            const tab = e.target.getAttribute('data-tab');
            this.activeTab = tab;
        },


    }
}