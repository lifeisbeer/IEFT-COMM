#This market maker uses moving averages and the crossover
#method to decide when to transact in the market
class Trader_COMM(Trader):
    def __init__(self, ttype, tid, balance, time):
        super().__init__(ttype, tid, balance, time)
        # ----- hyperparameters -----
        self.type = 1 #type is 1(shaver-like), 2(bid/ask at avg) or 3(bid/ask at market)
        self.ma_type = 'E' #E: exponential, W: weighted, S: simple
        self.short = 2 #short moving average window
        self.long = 8 #long moving average window
        self.profit = 1.6 #target profit
        self.loss = 0.7 #max loss willing to take
        # ---------------------------
        self.mem = (0, 0)
        self.bid_order = None
        self.ask_order = None
        self.latest = 0
        self.own = 0
        self.last_purchase_price = None
        self.last_sell_price = None
        self.net_worth = 0

    def respond(self, time, lob, trade, verbose):
        mvaShort = 0
        countShort = 0
        mvaLong = 0
        countLong = 0

        for t in reversed(lob["tape"]):
            if t['type'] == 'Trade':
                if countShort == 0:
                    self.latest = t['price']

                if countShort < self.short:
                    if self.ma_type == 'W':
                        mvaShort += t['price']*(self.short-countShort)
                    elif self.ma_type == 'S':
                        mvaShort += t['price']
                    countShort += 1

                if countLong < self.long:
                    if self.ma_type == 'W':
                        mvaLong += t['price']*(self.long-countLong)
                    elif self.ma_type == 'S':
                        mvaLong += t['price']
                    countLong += 1
                else:
                    break

        #if no trades happened set averages to None, don't send order
        if countShort == 0:
            mvaShort = None
            mvaLong = None
            # we don't have enough information to buy or to sell
            # wait for more trades to gain inside, then trade
        else:
            #find moving averages
            if self.ma_type == 'E':
                if self.mem == (0, 0): #first trade
                    mvaShort = self.latest
                    mvaLong = self.latest
                else:
                    facShort = 2/(1+self.short)
                    facLong = 2/(1+self.long)
                    mvaShort = self.latest*facShort + self.mem[0]*(1-facShort)
                    mvaLong = self.latest*facLong + self.mem[1]*(1-facLong)
            elif self.ma_type == 'W':
                denShort = (countShort*(countShort+1))/2
                denLong = (countLong*(countLong+1))/2
                mvaShort = mvaShort/denShort
                mvaLong = mvaLong/denLong
            elif self.ma_type == 'S':
                mvaShort = mvaShort/countShort
                mvaLong = mvaLong/countLong
            else:
                sys.exit('Wrong moving average type.')

            if self.mem != (mvaShort, mvaLong): #if averages have changed (trade happened)
                mvaShortPr = self.mem[0] #store previous value of short
                mvaLongPr = self.mem[1] #store previous value of long
                self.mem = (mvaShort, mvaLong) #update values

                #crossover method
                if mvaShort > mvaLong: #check if crossing upwards
                    if mvaShortPr <= mvaLongPr:
                        #since price is crossing upwards, then it's good time to buy
                        if self.type == 1: #type 1 works like shaver
                            if lob['bids']['best'] == None:
                                p = 1
                            else:
                                p = lob['bids']['best'] + 1
                        elif self.type == 2: #type 2 orders at the current average
                            p = mvaLong
                        elif self.type == 3: #type 3 just buys at market price
                            if lob['asks']['best'] == None:
                                p = 1
                            else:
                                p = lob['asks']['best'] + 1
                        else:
                            sys.exit('Wrong trade type.')

                        if not self.last_sell_price == None:
                            if p > self.last_sell_price: #make sure we don't lose money
                                p = self.last_sell_price

                        if self.balance >= p:
                            oprice = p
                        else: #if you can't make a better bid than the best, make the best you can
                            oprice = self.balance
                        self.bid_order = Order(self.tid, 'Bid', oprice, 1, time, lob['QID'])

                        if self.ask_order == None:
                            self.orders = [self.bid_order]
                        else:
                            self.orders = [self.bid_order, self.ask_order]
                elif mvaShort < mvaLong: #check if crossing downwards
                    if mvaShortPr >= mvaLongPr:
                        #since price is crossing downwards, then it's a good time to sell
                        if self.own >= 1:
                            if self.type == 1: #type 1 makes a better ask than the current best
                                if lob['asks']['best'] == None:
                                    p = 999
                                else:
                                    p = lob['asks']['best'] - 1
                            elif self.type == 2: #type 2 orders at the current average
                                p = mvaShort
                            elif self.type == 3: #type 3 makes a market order
                                if lob['bids']['best'] == None:
                                    p = 999
                                else:
                                    p = lob['bids']['best']
                            else:
                                sys.exit('Wrong trade type.')

                            if not self.last_purchase_price == None:
                                if p < self.last_purchase_price: #make sure we don't lose money
                                    p = self.last_purchase_price
                            self.ask_order = Order(self.tid, 'Ask', p, 1, time, lob['QID'])

                            if self.bid_order == None:
                                self.orders = [self.ask_order]
                            else:
                                self.orders = [self.ask_order, self.bid_order]
                elif self.own > 0: #sell if you have enough profit/loss
                    if not lob['bids']['best'] == None:
                        if self.last_purchase_price*self.profit >= lob['bids']['best']:
                            self.ask_order = Order(self.tid, 'Ask', lob['bids']['best'], 1, time, lob['QID'])
                            if self.bid_order == None:
                                self.orders = [self.ask_order]
                            else:
                                self.orders = [self.ask_order, self.bid_order]
                        elif self.last_purchase_price*self.loss >= mvaShort:
                            self.ask_order = Order(self.tid, 'Ask', lob['bids']['best'], 1, time, lob['QID'])
                            if self.bid_order == None:
                                self.orders = [self.ask_order]
                            else:
                                self.orders = [self.ask_order, self.bid_order]

    def getorder(self, time, countdown, lob):
        if len(self.orders) < 1:
            order = None
        else:
            order = Order(self.tid, self.orders[0].otype, self.orders[0].price, 1, time, lob['QID'])
            self.lastquote = self.orders[0].price
        return order

    def bookkeep(self, trade, order, verbose, time):
        self.blotter.append(trade)  # add trade record to trader's blotter
        #find order in my orders
        if len(self.orders) == 1: #only one order
            i = 0
        elif order.tid == self.tid: #this is my order
            if order.otype == 'Bid':
                if self.orders[0].otype == 'Bid': i = 0
                else: i = 1
            elif order.otype == 'Ask':
                if self.orders[0].otype == 'Ask': i = 0
                else: i = 1
        else: #it's someone else order
            if order.otype == 'Bid':
                if self.orders[0].otype == 'Ask': i = 0
                else: i = 1
            elif order.otype == 'Ask':
                if self.orders[0].otype == 'Bid': i = 0
                else: i = 1

        if self.orders[i].otype == 'Bid':
            self.bid_order = None
            self.balance -= trade['price']
            self.last_purchase_price = trade['price']
            self.own += 1
        elif self.orders[i].otype == 'Ask':
            self.ask_order = None
            self.balance += trade['price']
            self.last_sell_price = trade['price']
            self.own -= 1

        self.n_trades += 1

        self.net_worth = self.balance + self.last_purchase_price * self.own

        if verbose:
            outstr = ""
            for order in self.orders:
                outstr = outstr + str(order)
            if self.orders[i].otype == 'Bid': # We bought some shares
                outcome = "Bght"
            else: # We sold some shares
                outcome = "Sold"
            print('%s, %s=%d; Qty=%d; Balance=%d, NetWorth=%d'
                 %(outstr, outcome, trade['price'], self.own, self.balance, self.net_worth))
        self.del_order(self.orders[i])  # delete the order
        #print(self.orders)

    def del_order(self, order):
        self.orders.remove(order)
