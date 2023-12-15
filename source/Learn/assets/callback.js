// assets/app.js
if (!window.dash_clientside) {
    window.dash_clientside = {};
}
window.dash_clientside.clientside = {
    open_tab: function(clickData) {
        if (clickData) {
            const point_url = clickData['points'][0]['customdata'];
            if (point_url) {
                window.open(point_url, '_blank');
            }
        }
        return null;
    }
};
