import minizinc
from pulp import*
import numpy as np
from models.PulpResult import PulpResult


def OptimizeCase1(num_item, maxitemcount, cardnumberList, CostMatrix):
    '''
    num_item : number of item which is different
    maxitemcount : the maximum number of same item.
    cardnumberList : the number of each item we want
    CostMatrix : the price of each item

    Split each item into one quantity of each item, so "costs" means each item's price.
    And we want to get "x" means each item we want or not, "x" is a binary list of list
    such that sum(x[i]) = cardnumberList[i], this mean item A I need cardnumberList['A'] number, and "x['A']" will set the cheapest of cardnumberList['A'] number to 1 and others to 0.
    '''    
    model = minizinc.Model()
    model.add_string("""
int: num_item;
int: maxitemcount;
% total price
var int: total; 

solve minimize total;
% solve satisfy;

array[1..num_item] of int: cardnumberList;
array[1..num_item, 1..maxitemcount] of int: costs;
array[1..num_item,1..maxitemcount] of var 0..1: x;
                 
constraint forall(i in 1..num_item) (sum(j in 1..maxitemcount)(x[i, j]) = cardnumberList[i])
/\ 
total = sum(i in 1..num_item)(sum(j in 1..maxitemcount)(costs[i, j] * x[i, j]))

""")
    # Transform Model into a instance
    gecode = minizinc.Solver.lookup("gecode")
    inst = minizinc.Instance(gecode, model)
    inst["num_item"] = num_item
    inst["maxitemcount"] = int(maxitemcount)
    inst["cardnumberList"] = cardnumberList
    inst["costs"] = CostMatrix
    return inst.solve()

def OptimizeCase2(num_item, shop_count, cardnumberList, maxitemcount, PriceMatrix, QtyMatrix):
    '''
    num_item : number of item which is different
    shop_count : number of shop
    shop_item : set each shop at least 3 item with different cost
    cardnumberList : the number of each item we want
    maxitemcount : maximum value in cardnumberList
    PriceMatrix : the price of each item
    QtyMatrix : the quantity of each item

    In this case, we make 3d matrix with x:different item y:shop z:each shop at least 3 item, 
    we group each item by shop such that if item in that shop has been selected, we gain delivery cost.
    "x" is a list of list of list mean each item need to buy, "x[i]" is equal to cardnumberList[i] 
    but each element is less than QtyMatrix(you can't buy more than that shop has).
    '''
    model = minizinc.Model()
    model.add_string("""
int: num_item;
int: shop_count;
int: shop_item = 3;
int: maxitemcount;
% total price
var int: total; 

solve minimize total;
% solve satisfy;

array[1..num_item] of int: cardnumberList;
array[1..num_item, 1..shop_count, 1..shop_item] of int: PriceMatrix;
array[1..num_item, 1..shop_count, 1..shop_item] of int: QtyMatrix;
array[1..num_item,1..shop_count, 1..shop_item] of var 0..maxitemcount: x;
                 
constraint forall (i in 1..num_item, j in 1..shop_count, k in 1..shop_item) (
    x[i, j, k] <= QtyMatrix[i, j, k]
);
constraint forall(i in 1..num_item) (sum(j in 1..shop_count, k in 1..shop_item)(x[i, j, k]) = cardnumberList[i])
/\ 
total = sum(i in 1..num_item, j in 1..shop_count, k in 1..shop_item)(PriceMatrix[i, j, k] * x[i, j, k])+
sum(j in 1..shop_count)(let {var int: this_cost = sum(i in 1..num_item, k in 1..shop_item)(x[i,j,k])} in 60*bool2int(this_cost > 0))

""")
    # Transform Model into a instance
    gecode = minizinc.Solver.lookup("gecode")
    inst = minizinc.Instance(gecode, model)
    inst["num_item"] = num_item
    inst["shop_count"] = int(shop_count)
    inst["cardnumberList"] = cardnumberList
    inst["maxitemcount"] = maxitemcount
    inst["PriceMatrix"] = PriceMatrix
    inst["QtyMatrix"] = QtyMatrix
    return inst.solve()

def OptimizeCase3(num_item, shop_count, cardnumberList, maxitemcount, PriceMatrix, QtyMatrix):
    model = pulp.LpProblem("value_min", pulp.const.LpMinimize)
    indexs = [(i, j, k) for i in range(num_item) for j in range(shop_count) for k in range(3)]
    result = pulp.LpVariable.dicts("result", indices = indexs, cat = "Integer")
    column_sums_flags = pulp.LpVariable.dicts("column_sum_flag", range(shop_count), cat="Binary")
    
    for i in range(num_item):
        for j in range(shop_count):
            for k in range(3): 
                result[i, j, k].lowBound = 0
                result[i, j, k].upBound = maxitemcount
                model += result[i, j, k] <= QtyMatrix[i, j, k]
    for i in range(num_item):
        model += pulp.lpSum(result[i, j, k] for j in range(shop_count) for k in range(3)) == cardnumberList[i]
        
    big_m = 1000000
    for j in range(shop_count):
        col_sum = pulp.lpSum(result[i, j, k] for i in range(num_item) for k in range(3))
        model += col_sum <= column_sums_flags[j] * big_m
        model += col_sum >= column_sums_flags[j]

    model += pulp.lpSum(PriceMatrix[i, j, k] * result[i, j, k] for i in range(num_item) for j in range(shop_count) for k in range(3)) + 60 * pulp.lpSum(column_sums_flags[j] for j in range(shop_count)) #目標函數
    model.solve()

    for var in model.variables():
        # if var.name == 'column_sum_flag':
        #     print(f"{var.name}: {var.value()}")

        if var.value() > 0 and var.name[0:6] == 'result':
            print(f"{var.name}: {var.value()}")

        if var.value() == 1 and var.name[0:15] == 'column_sum_flag':
            print(f"{var.name}: {var.value()}")
    return PulpResult(model.objective.value(), result)