class StockTradingEngine:
  def __init__(self):
    self.buy_orders = [[] for i in range(1024)] #goal is to use a hashing mechanism to index into the list (like a dictionary)
    self.sell_orders = [[] for i in range(1024)]
    self.lock = 0

  def hashingAlg(self, ticker): # hash ticker to an index for O(1) array lookup
    sum = 0
    for c in ticker:
      sum += ord(c)
    return sum % 1024

  def acquire_lock(self):
    while self.lock: #do not allow if already locked, and keep waiting for lock to be released before giving to another thread
        pass
    self.lock = 1

  def release_lock(self):
    self.lock = 0


  def addOrder(self, order_type, ticker_symbol, quantity, price):
    index = self.hashingAlg(ticker_symbol)

    self.acquire_lock()

    if order_type == 'Buy':   #sort buy in descending order (will help us run matchorder in O(n) time)
      i = 0
      while i < len(self.buy_orders[index]) and self.buy_orders[index][i][1] > price: #go into tuple and check price
          i += 1
      self.buy_orders[index].insert(i, (ticker_symbol, price, quantity)) #add in the ticker in the tuple just in case hashing algorithm has hash collisions
            
    else:  ##sort sells in descending order 
      i = 0
      while i < len(self.sell_orders[index]) and self.sell_orders[index][i][1] < price:
          i += 1
      self.sell_orders[index].insert(i, (ticker_symbol, price, quantity))

    self.release_lock()
    self.matchOrder(index, ticker_symbol)


  def matchOrder(self, index, ticker_symbol):
    self.acquire_lock()  

    buy_queue = []
    for order in range(len(self.buy_orders[index])):
        if self.buy_orders[index][order][0] == ticker_symbol: #check hash collisions
          buy_queue.append(order)

    sell_queue = []
    for order in range(len(self.sell_orders[index])):
        if self.sell_orders[index][order][0] == ticker_symbol:
          sell_queue.append(order)
  
    while buy_queue and sell_queue: 
        buyindex = buy_queue[0]
        sellindex = sell_queue[0]
        ticker, buy_price, buy_qty = self.buy_orders[index][buyindex]
        print(self.sell_orders[index][sellindex])
        ticker, sell_price, sell_qty = self.sell_orders[index][sellindex]

        if buy_price >= sell_price:  #given matching condition
            print('mathc')
            traded_qty = min(buy_qty, sell_qty)
            buy_qty -= traded_qty
            sell_qty -= traded_qty

            if buy_qty > 0:
                self.buy_orders[index][buyindex] = (ticker_symbol, buy_price, buy_qty)  #if order still has quantity left, update the qty
                buy_queue[0] = (ticker_symbol, buy_price, buy_qty)
            else:
                self.buy_orders[index].pop(buyindex)  #if no qty left, remove the order
                buy_queue.pop(0)

            if sell_qty > 0:
                self.sell_orders[index][sellindex] = (ticker_symbol, sell_price, sell_qty)
                sell_queue[0] = (ticker_symbol, sell_price, sell_qty)
            else:
                self.sell_orders[index].pop(sellindex)
                sell_queue.pop(0)
        else:
            break  # no further matches possible; if highest buy isn't >= lowest sell, the other in betweens won't fit the matching condition either

    self.release_lock()


#Wrapper for testing
def test_stock_engine():
    engine = StockTradingEngine()
    
    
    engine.addOrder("Buy", "AAPL", 10, 150)   #buy appl at 150
    engine.addOrder("Sell", "AAPL", 5, 145)   #sell at $145 (should match with above)
    engine.addOrder("Sell", "AAPL", 10, 155)  #sell at $155 (should not match)

    engine.addOrder("Buy", "GOOGL", 20, 2800)
    engine.addOrder("Sell", "GOOGL", 20, 2795)  #should match

    print("Remaining Buy Orders:", engine.buy_orders)
    print("Remaining Sell Orders:", engine.sell_orders)

test_stock_engine()

