var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.resultLinkScenario = function (props) {
    /* Return an empty span if props.value is '', representing an incomplete simulation,
    else return a link to the results page (single scenario) */
    if (props.value === '') {
        return React.createElement('span', {}, '')
    }
    return React.createElement('a',
    {
        href: '/hpath/view/single/' + props.value
    }, 'Results')
}
