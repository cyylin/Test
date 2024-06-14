class SearchResult(object):
    def __init__(self, TotalRows, Rows, LimitedTotalRows):
        self.TotalRows = TotalRows
        self.Rows = Rows
        self.LimitedTotalRows = LimitedTotalRows
    
    def dict2SearchResult(d):
        if 'TotalRows' in d and 'Rows' in d and 'LimitedTotalRows' in d:
            return SearchResult(d['TotalRows'], d['Rows'], d['LimitedTotalRows'])
        return d